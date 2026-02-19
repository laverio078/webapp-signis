import unittest
from unittest.mock import patch, MagicMock
from app import app

class TestSIGNISAppExtensive(unittest.TestCase):

    def setUp(self):
        """Configurazione iniziale eseguita prima di ogni singolo test"""
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'chiave_test_sicura'
        self.client = app.test_client()

    def _setup_mock_db(self, mock_get_db_connection, fetchone_data=None, fetchall_data=None):
        """
        Helper avanzato: gestisce sia fetchone che fetchall.
        Se passiamo liste, simula chiamate multiple (utile per le tendine nei form).
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        
        if isinstance(fetchone_data, list):
            mock_cursor.fetchone.side_effect = fetchone_data
        else:
            mock_cursor.fetchone.return_value = fetchone_data

        # Gestione fetchall (es. per liste principali o tendine)
        if isinstance(fetchall_data, list) and len(fetchall_data) > 0 and isinstance(fetchall_data[0], list):
            mock_cursor.fetchall.side_effect = fetchall_data
        else:
            mock_cursor.fetchall.return_value = fetchall_data or []
            
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = mock_conn
        return mock_conn, mock_cursor


    @patch('app.get_db_connection')
    def test_01_dashboard_numeri(self, mock_db):
        self._setup_mock_db(mock_db, fetchone_data=[[5], [12], [8], [2]])
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'12', response.data) # Verifica asset
        self.assertIn(b'2', response.data)  # Verifica servizi critici


    @patch('app.get_db_connection')
    def test_02_org_read(self, mock_db):
        dati = [{'organization_id': '1', 'name': 'Org Alpha', 'vat': '123', 'address': 'Roma', 'contact_email': 'a@a.it', 'contact_phone': '111'}]
        self._setup_mock_db(mock_db, fetchall_data=dati)
        response = self.client.get('/organizations')
        self.assertIn(b'Org Alpha', response.data)

    @patch('app.get_db_connection')
    def test_03_org_create(self, mock_db):
        mock_conn, _ = self._setup_mock_db(mock_db)
        form_data = {'name': 'Nuova Org', 'vat': '000', 'address': 'Milano', 'contact_email': 't@t.it', 'contact_phone': '000'}
        response = self.client.post('/save_org', data=form_data, follow_redirects=True)
        self.assertTrue(mock_conn.commit.called)
        self.assertIn(b'Nuova organizzazione creata!', response.data)

    @patch('app.get_db_connection')
    def test_04_org_update(self, mock_db):
        mock_conn, _ = self._setup_mock_db(mock_db, fetchone_data={'name': 'Vecchia Org'})
        form_data = {'name': 'Org Aggiornata', 'vat': '000', 'address': 'Milano', 'contact_email': 't@t.it', 'contact_phone': '000'}
        response = self.client.post('/save_org/1', data=form_data, follow_redirects=True)
        self.assertTrue(mock_conn.commit.called)
        self.assertIn(b'Organizzazione aggiornata!', response.data)

    @patch('app.get_db_connection')
    def test_05_org_delete(self, mock_db):
        mock_conn, _ = self._setup_mock_db(mock_db)
        response = self.client.get('/delete_org/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_conn.commit.called)
        self.assertIn(b'Organizzazione eliminata.', response.data)


    @patch('app.get_db_connection')
    def test_06_person_read(self, mock_db):
        dati = [{'person_id': '1', 'given_name': 'Mario', 'family_name': 'Rossi', 'email': 'm@r.it', 'phone': '', 'org_name': 'Azienda'}]
        self._setup_mock_db(mock_db, fetchall_data=dati)
        response = self.client.get('/persons')
        self.assertIn(b'Rossi Mario', response.data)

    @patch('app.get_db_connection')
    def test_07_person_create(self, mock_db):
        mock_conn, _ = self._setup_mock_db(mock_db)
        form_data = {'given_name': 'L', 'family_name': 'V', 'email': 'l@v.it', 'phone': '', 'metadata': '{}', 'organization_id': '1'}
        response = self.client.post('/save_person', data=form_data, follow_redirects=True)
        self.assertTrue(mock_conn.commit.called)

    @patch('app.get_db_connection')
    def test_08_person_update(self, mock_db):
        mock_conn, _ = self._setup_mock_db(mock_db, fetchone_data={'given_name': 'Vecchio'})
        form_data = {'given_name': 'Nuovo', 'family_name': 'Rossi', 'email': 'x@x.it', 'phone': '', 'metadata': '{}', 'organization_id': '1'}
        response = self.client.post('/save_person/1', data=form_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_conn.commit.called)
        self.assertIn(b'Persona aggiornata', response.data)

    @patch('app.get_db_connection')
    def test_09_person_delete(self, mock_db):
        mock_conn, _ = self._setup_mock_db(mock_db)
        response = self.client.get('/delete_person/1', follow_redirects=True)
        self.assertTrue(mock_conn.commit.called)
        self.assertIn(b'Persona eliminata', response.data)


    @patch('app.get_db_connection')
    def test_10_role_create(self, mock_db):
        mock_conn, _ = self._setup_mock_db(mock_db)
        form_data = {'code': 'CISO', 'description': 'Chief Info Security Officer'}
        response = self.client.post('/save_role', data=form_data, follow_redirects=True)
        self.assertTrue(mock_conn.commit.called)

    @patch('app.get_db_connection')
    def test_11_role_update_and_delete(self, mock_db):
        mock_conn, _ = self._setup_mock_db(mock_db, fetchone_data={'code': 'OLD'})
        # Update
        response_upd = self.client.post('/save_role/1', data={'code': 'NEW', 'description': 'Desc'}, follow_redirects=True)
        self.assertTrue(mock_conn.commit.called)
        self.assertIn(b'Ruolo modificato', response_upd.data)
        # Delete
        response_del = self.client.get('/delete_role/1', follow_redirects=True)
        self.assertIn(b'Ruolo eliminato', response_del.data)

    @patch('app.get_db_connection')
    def test_12_asset_read(self, mock_db):
        dati = [{'asset_id': '1', 'name': 'Firewall X', 'asset_type': 'Hardware', 'criticality': 5, 'org_name': 'Azienda'}]
        self._setup_mock_db(mock_db, fetchall_data=dati)
        response = self.client.get('/assets')
        self.assertIn(b'Firewall X', response.data)

    @patch('app.get_db_connection')
    def test_13_asset_create_and_update(self, mock_db):
        mock_conn, _ = self._setup_mock_db(mock_db)
        form_data = {'name': 'Server DB', 'type': 'Hardware', 'org': '1', 'criticality': '4', 'lifecycle_status': 'active'}
        
        resp_insert = self.client.post('/save_asset', data=form_data, follow_redirects=True)
        self.assertIn(b'Nuovo asset inserito!', resp_insert.data)
        
        resp_update = self.client.post('/save_asset/1', data=form_data, follow_redirects=True)
        self.assertIn(b'Asset aggiornato con successo!', resp_update.data)

    @patch('app.get_db_connection')
    def test_14_asset_delete(self, mock_db):
        mock_conn, _ = self._setup_mock_db(mock_db)
        response = self.client.get('/delete_asset/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_conn.commit.called)
        self.assertIn(b'Asset eliminato', response.data)


    @patch('app.get_db_connection')
    def test_15_vendor_crud(self, mock_db):
        mock_conn, _ = self._setup_mock_db(mock_db)
        # Create
        form_data = {'name': 'CloudCorp', 'contact_name': 'Anna', 'contact_email': 'a@cloud.it', 'contact_phone': '', 'metadata': '{}'}
        resp_c = self.client.post('/save_vendor', data=form_data, follow_redirects=True)
        self.assertIn(b'Fornitore salvato', resp_c.data)
        
        # Update
        resp_u = self.client.post('/save_vendor/1', data=form_data, follow_redirects=True)
        self.assertIn(b'Fornitore aggiornato', resp_u.data)

        # Delete
        resp_d = self.client.get('/delete_vendor/1', follow_redirects=True)
        self.assertIn(b'Fornitore eliminato', resp_d.data)


    @patch('app.get_db_connection')
    def test_16_service_crud(self, mock_db):
        mock_conn, _ = self._setup_mock_db(mock_db, fetchone_data={'name': 'Old Srv'}, fetchall_data=[])
        form_data = {'name': 'ERP', 'description': 'Gest', 'organization_id': '1', 'service_owner': '', 'criticality': '5', 'business_impact': 'Alto'}
        
        # Create
        resp_c = self.client.post('/save_service', data=form_data, follow_redirects=True)
        self.assertIn(b'Servizio salvato', resp_c.data)
        
        # Update
        resp_u = self.client.post('/save_service/1', data=form_data, follow_redirects=True)
        self.assertIn(b'Servizio aggiornato', resp_u.data)

        # Delete
        resp_d = self.client.get('/delete_service/1', follow_redirects=True)
        self.assertIn(b'Servizio eliminato', resp_d.data)


    @patch('app.get_db_connection')
    def test_17_service_asset_create_and_delete(self, mock_db):
        mock_conn, _ = self._setup_mock_db(mock_db, fetchall_data=[])
        # Create
        form_data = {'service_id': '1', 'asset_id': '1', 'role_in_service': 'Database Primary'}
        resp_c = self.client.post('/save_service_asset', data=form_data, follow_redirects=True)
        self.assertIn(b'Asset associato al Servizio!', resp_c.data)
        
        # Delete (Tabella associativa, due ID)
        resp_d = self.client.get('/delete_service_asset/1/1', follow_redirects=True)
        self.assertIn(b'Associazione rimossa', resp_d.data)


    @patch('app.get_db_connection')
    def test_18_dependency_crud(self, mock_db):
        mock_conn, _ = self._setup_mock_db(mock_db, fetchone_data={'description': 'Old'}, fetchall_data=[])
        form_data = {
            'service_id': '1', 'vendor_id': '1', 'description': 'Hosting VPS', 
            'dependency_type': 'IaaS', 'sla_reference': '99.9%', 'criticality': '4'
        }
        # Create
        resp_c = self.client.post('/save_dependency', data=form_data, follow_redirects=True)
        self.assertIn(b'Dipendenza salvata', resp_c.data)
        
        # Update
        resp_u = self.client.post('/save_dependency/1', data=form_data, follow_redirects=True)
        self.assertIn(b'Dipendenza aggiornata', resp_u.data)
        
        # Delete
        resp_d = self.client.get('/delete_dependency/1', follow_redirects=True)
        self.assertIn(b'Dipendenza di supply chain eliminata', resp_d.data)

    @patch('app.get_db_connection')
    def test_19_compliance_crud(self, mock_db):
        mock_conn, _ = self._setup_mock_db(mock_db, fetchone_data={'gap_analysis': 'Old'}, fetchall_data=[])
        
        # Lettura
        response_get = self.client.get('/compliance')
        self.assertEqual(response_get.status_code, 200)

        # Creazione
        form_data = {
            'asset_id': '1', 'subcategory_code': 'PR.AC-1', 'status_current': 'Non Implementato', 
            'implementation_tier_current': '1', 'implementation_tier_target': '4', 'gap_analysis': 'Tutto da fare'
        }
        resp_post = self.client.post('/save_profile', data=form_data, follow_redirects=True)
        self.assertIn(b'Nuovo controllo ACN mappato', resp_post.data)

        # Modifica
        resp_upd = self.client.post('/save_profile/1', data=form_data, follow_redirects=True)
        self.assertIn(b'Profilo di sicurezza aggiornato', resp_upd.data)

        # Cancellazione
        resp_del = self.client.get('/delete_profile/1', follow_redirects=True)
        self.assertIn(b'Profilo di compliance eliminato', resp_del.data)


if __name__ == '__main__':
    unittest.main(verbosity=2)