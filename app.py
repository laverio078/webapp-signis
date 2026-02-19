from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
import psycopg2.extras

app = Flask(__name__)
app.secret_key = 'sk_live_WgGepnrmzBxTP8HmMKceRY4lf3Alt318' 

DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "admin"
DB_PASS = "adminpassword"
DB_PORT = "5432"

def get_db_connection():
    """Gestisce la connessione al database con lo schema corretto"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT,
            
            options="-c search_path=nis2,public"
        )
        return conn
    except Exception as e:
        print(f"ERRORE CONNESSIONE DB: {e}")
        return None




@app.route('/')
def index():
    conn = get_db_connection()
    if not conn:
        return "Errore di connessione al Database! Controlla Docker."
    
    cur = conn.cursor()
    
    cur.execute("SELECT count(*) FROM organization")
    o = cur.fetchone()[0]
    
    cur.execute("SELECT count(*) FROM asset")
    a = cur.fetchone()[0]
    
    cur.execute("SELECT count(*) FROM service")
    s_tot = cur.fetchone()[0]

    cur.execute("SELECT count(*) FROM service WHERE criticality >= 4")
    s_crit = cur.fetchone()[0]

    conn.close()
    return render_template('index.html', o=o, a=a, s_tot=s_tot, s_crit=s_crit)




@app.route('/organizations')
def lista_org():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM organization ORDER BY name")
    orgs = cur.fetchall()
    conn.close()
    return render_template('organizations.html', orgs=orgs)

@app.route('/save_org', methods=('GET', 'POST'))
@app.route('/save_org/<string:id>', methods=('GET', 'POST'))
def save_org(id=None):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    org = None
    
    if id:
        cur.execute("SELECT * FROM organization WHERE organization_id = %s", (id,))
        org = cur.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        vat = request.form['vat']
        address = request.form['address']
        contact_email = request.form['contact_email'] 
        contact_phone = request.form['contact_phone'] 
        
        try:
            if id:
                cur.execute("""
                    UPDATE organization 
                    SET name=%s, vat=%s, address=%s, contact_email=%s, contact_phone=%s 
                    WHERE organization_id=%s
                """, (name, vat, address, contact_email, contact_phone, id))
                flash('Organizzazione aggiornata!', 'success')
            else:
                cur.execute("""
                    INSERT INTO organization (name, vat, address, contact_email, contact_phone) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (name, vat, address, contact_email, contact_phone))
                flash('Nuova organizzazione creata!', 'success')
            conn.commit()
            return redirect(url_for('lista_org'))
        except Exception as e:
            conn.rollback()
            flash(f"Errore: {e}", 'danger')

    conn.close()
    return render_template('form_org.html', org=org)



@app.route('/persons')
def lista_persons():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT p.*, o.name as org_name 
        FROM person p 
        LEFT JOIN organization o ON p.organization_id = o.organization_id
        ORDER BY p.family_name
    """)
    persons = cur.fetchall()
    conn.close()
    return render_template('persons.html', persons=persons)

@app.route('/save_person', methods=('GET', 'POST'))
@app.route('/save_person/<string:id>', methods=('GET', 'POST'))
def save_person(id=None):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    person = None
    
    if id:
        cur.execute("SELECT * FROM person WHERE person_id = %s", (id,))
        person = cur.fetchone()

    if request.method == 'POST':
        nome = request.form['given_name']
        cognome = request.form['family_name']
        email = request.form['email']
        phone = request.form['phone'] 
        
        metadata = request.form['metadata'] or '{}' 
        org_id = request.form['organization_id']
        
        try:
            if id:
                cur.execute("""
                    UPDATE person 
                    SET given_name=%s, family_name=%s, email=%s, phone=%s, metadata=%s, organization_id=%s 
                    WHERE person_id=%s
                """, (nome, cognome, email, phone, metadata, org_id, id))
                flash('Persona aggiornata!', 'success')
            else:
                cur.execute("""
                    INSERT INTO person (given_name, family_name, email, phone, metadata, organization_id) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (nome, cognome, email, phone, metadata, org_id))
                flash('Nuova persona inserita!', 'success')
            conn.commit()
            return redirect(url_for('lista_persons'))
        except Exception as e:
            conn.rollback()
            flash(f"Errore di salvataggio (il metadato è un JSON valido?): {e}", 'danger')

    cur.execute("SELECT organization_id, name FROM organization ORDER BY name")
    orgs = cur.fetchall()
    conn.close()
    return render_template('form_person.html', person=person, orgs=orgs)

@app.route('/delete_person/<string:id>')
def delete_person(id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM person WHERE person_id = %s", (id,))
        conn.commit()
        flash('Persona eliminata.', 'warning')
    except Exception as e:
        conn.rollback()
        flash(f"Errore: {e}", 'danger')
    conn.close()
    return redirect(url_for('lista_persons'))




@app.route('/roles')
def lista_roles():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM role ORDER BY code")
    roles = cur.fetchall()
    conn.close()
    return render_template('roles.html', roles=roles)

@app.route('/save_role', methods=('GET', 'POST'))
@app.route('/save_role/<string:id>', methods=('GET', 'POST'))
def save_role(id=None):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    role = None
    
    if id:
        cur.execute("SELECT * FROM role WHERE role_id = %s", (id,))
        role = cur.fetchone()

    if request.method == 'POST':
        code = request.form['code']
        desc = request.form['description']
        
        try:
            if id:
                cur.execute("UPDATE role SET code=%s, description=%s WHERE role_id=%s", (code, desc, id))
                flash('Ruolo modificato.', 'success')
            else:
                cur.execute("INSERT INTO role (code, description) VALUES (%s, %s)", (code, desc))
                flash('Nuovo ruolo creato.', 'success')
            conn.commit()
            return redirect(url_for('lista_roles'))
        except Exception as e:
            conn.rollback()
            flash(f"Errore: {e}", 'danger')

    conn.close()
    return render_template('form_role.html', role=role)




@app.route('/assets')
def lista_assets():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT a.*, o.name as org_name 
        FROM asset a 
        JOIN organization o ON a.organization_id = o.organization_id
        ORDER BY a.name
    """)
    assets = cur.fetchall()
    conn.close()
    return render_template('assets.html', assets=assets)

@app.route('/save_asset', methods=('GET', 'POST'))
@app.route('/save_asset/<string:id>', methods=('GET', 'POST'))
def save_asset(id=None):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    asset = None
    
    if id:
        cur.execute("SELECT * FROM asset WHERE asset_id = %s", (id,))
        asset = cur.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        tipo = request.form['type']
        org_id = request.form['org']
        crit = request.form['criticality']
        status = request.form['lifecycle_status']
        
        try:
            if id:
                cur.execute("""
                    UPDATE asset 
                    SET name=%s, asset_type=%s, organization_id=%s, criticality=%s, lifecycle_status=%s
                    WHERE asset_id=%s
                """, (name, tipo, org_id, crit, status, id))
                flash('Asset aggiornato con successo!', 'success')
            else:
                cur.execute("""
                    INSERT INTO asset (name, asset_type, organization_id, criticality, lifecycle_status, identifier)
                    VALUES (%s, %s, %s, %s, %s, 'N/A')
                """, (name, tipo, org_id, crit, status))
                flash('Nuovo asset inserito!', 'success')
            conn.commit()
            return redirect(url_for('lista_assets'))
        except Exception as e:
            conn.rollback()
            flash(f"Errore salvataggio: {e}", 'danger')

    cur.execute("SELECT organization_id, name FROM organization ORDER BY name")
    orgs = cur.fetchall()
    conn.close()
    return render_template('form_asset.html', asset=asset, organizations=orgs)

@app.route('/delete_asset/<string:id>')
def delete_asset(id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM asset WHERE asset_id = %s", (id,))
        conn.commit()
        flash('Asset eliminato.', 'warning')
    except Exception as e:
        conn.rollback()
        flash(f"Non posso eliminare l'asset: {e}", 'danger')
    conn.close()
    return redirect(url_for('lista_assets'))




@app.route('/vendors')
def lista_vendors():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM vendor ORDER BY name")
    vendors = cur.fetchall()
    conn.close()
    return render_template('vendors.html', vendors=vendors)

@app.route('/save_vendor', methods=('GET', 'POST'))
@app.route('/save_vendor/<string:id>', methods=('GET', 'POST'))
def save_vendor(id=None):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    vendor = None
    
    if id:
        cur.execute("SELECT * FROM vendor WHERE vendor_id = %s", (id,))
        vendor = cur.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        c_name = request.form['contact_name']
        c_email = request.form['contact_email']
        c_phone = request.form['contact_phone']
        
        metadata = request.form['metadata'] or '{}'
        
        try:
            if id:
                cur.execute("""
                    UPDATE vendor 
                    SET name=%s, contact_name=%s, contact_email=%s, contact_phone=%s, metadata=%s 
                    WHERE vendor_id=%s
                """, (name, c_name, c_email, c_phone, metadata, id))
                flash('Fornitore aggiornato.', 'success')
            else:
                cur.execute("""
                    INSERT INTO vendor (name, contact_name, contact_email, contact_phone, metadata) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (name, c_name, c_email, c_phone, metadata))
                flash('Fornitore salvato.', 'success')
            conn.commit()
            return redirect(url_for('lista_vendors'))
        except Exception as e:
            conn.rollback()
            flash(f"Errore di salvataggio (JSON valido?): {e}", 'danger')

    conn.close()
    return render_template('form_vendor.html', vendor=vendor)

@app.route('/delete_vendor/<string:id>')
def delete_vendor(id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM vendor WHERE vendor_id = %s", (id,))
        conn.commit()
        flash('Fornitore eliminato.', 'warning')
    except Exception as e:
        conn.rollback()
        flash(f"Impossibile eliminare (ha dipendenze collegate?): {e}", 'danger')
    conn.close()
    return redirect(url_for('lista_vendors'))




@app.route('/services')
def lista_services():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT s.*, o.name as org_name, p.family_name as owner_name 
        FROM service s
        JOIN organization o ON s.organization_id = o.organization_id
        LEFT JOIN person p ON s.service_owner = p.person_id
        ORDER BY s.name
    """)
    services = cur.fetchall()
    conn.close()
    return render_template('services.html', services=services)

@app.route('/save_service', methods=('GET', 'POST'))
@app.route('/save_service/<string:id>', methods=('GET', 'POST'))
def save_service(id=None):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    service = None
    
    if id:
        cur.execute("SELECT * FROM service WHERE service_id = %s", (id,))
        service = cur.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        desc = request.form['description']
        org_id = request.form['organization_id']
        owner_id = request.form['service_owner'] or None
        crit = request.form['criticality']
        impact = request.form['business_impact']
        
        try:
            if id:
                cur.execute("""
                    UPDATE service SET name=%s, description=%s, organization_id=%s, service_owner=%s, criticality=%s, business_impact=%s
                    WHERE service_id=%s
                """, (name, desc, org_id, owner_id, crit, impact, id))
                flash('Servizio aggiornato.', 'success')
            else:
                cur.execute("""
                    INSERT INTO service (name, description, organization_id, service_owner, criticality, business_impact)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (name, desc, org_id, owner_id, crit, impact))
                flash('Servizio salvato.', 'success')
            conn.commit()
            return redirect(url_for('lista_services'))
        except Exception as e:
            conn.rollback()
            flash(f"Errore: {e}", 'danger')

    cur.execute("SELECT organization_id, name FROM organization ORDER BY name")
    orgs = cur.fetchall()
    cur.execute("SELECT person_id, given_name, family_name FROM person ORDER BY family_name")
    persons = cur.fetchall()
    
    conn.close()
    return render_template('form_service.html', service=service, orgs=orgs, persons=persons)




@app.route('/service_assets')
def lista_service_assets():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT sa.*, s.name as service_name, a.name as asset_name 
        FROM service_asset sa
        JOIN service s ON sa.service_id = s.service_id
        JOIN asset a ON sa.asset_id = a.asset_id
        ORDER BY s.name, a.name
    """)
    links = cur.fetchall()
    conn.close()
    return render_template('service_assets.html', links=links)

@app.route('/save_service_asset', methods=('GET', 'POST'))
def save_service_asset():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':
        s_id = request.form['service_id']
        a_id = request.form['asset_id']
        role = request.form['role_in_service']
        
        try:
            cur.execute("""
                INSERT INTO service_asset (service_id, asset_id, role_in_service)
                VALUES (%s, %s, %s)
                ON CONFLICT (service_id, asset_id) DO UPDATE SET role_in_service = EXCLUDED.role_in_service
            """, (s_id, a_id, role))
            conn.commit()
            flash('Asset associato al Servizio!', 'success')
            return redirect(url_for('lista_service_assets'))
        except Exception as e:
            conn.rollback()
            flash(f"Errore associazione: {e}", 'danger')

    cur.execute("SELECT service_id, name FROM service ORDER BY name")
    services = cur.fetchall()
    cur.execute("SELECT asset_id, name FROM asset ORDER BY name")
    assets = cur.fetchall()
    
    conn.close()
    return render_template('form_service_asset.html', services=services, assets=assets)




@app.route('/dependencies')
def lista_dependencies():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT d.*, s.name as service_name, v.name as vendor_name 
        FROM dependency d
        JOIN service s ON d.service_id = s.service_id
        JOIN vendor v ON d.vendor_id = v.vendor_id
        ORDER BY s.name
    """)
    deps = cur.fetchall()
    conn.close()
    return render_template('dependencies.html', deps=deps)

@app.route('/save_dependency', methods=('GET', 'POST'))
@app.route('/save_dependency/<string:id>', methods=('GET', 'POST'))
def save_dependency(id=None):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    dep = None
    
    if id:
        cur.execute("SELECT * FROM dependency WHERE dependency_id = %s", (id,))
        dep = cur.fetchone()

    if request.method == 'POST':
        s_id = request.form['service_id']
        v_id = request.form['vendor_id']
        desc = request.form['description']
        type_dep = request.form['dependency_type']
        sla = request.form['sla_reference']
        crit = request.form['criticality']
        
        try:
            if id:
                cur.execute("""
                    UPDATE dependency SET service_id=%s, vendor_id=%s, description=%s, dependency_type=%s, sla_reference=%s, criticality=%s
                    WHERE dependency_id=%s
                """, (s_id, v_id, desc, type_dep, sla, crit, id))
                flash('Dipendenza aggiornata.', 'success')
            else:
                cur.execute("""
                    INSERT INTO dependency (service_id, vendor_id, description, dependency_type, sla_reference, criticality)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (s_id, v_id, desc, type_dep, sla, crit))
                flash('Dipendenza salvata.', 'success')
            conn.commit()
            return redirect(url_for('lista_dependencies'))
        except Exception as e:
            conn.rollback()
            flash(f"Errore: {e}", 'danger')

    cur.execute("SELECT service_id, name FROM service ORDER BY name")
    services = cur.fetchall()
    cur.execute("SELECT vendor_id, name FROM vendor ORDER BY name")
    vendors = cur.fetchall()
    
    conn.close()
    return render_template('form_dependency.html', dep=dep, services=services, vendors=vendors)



# Questa me la stavo a scordà.

@app.route('/compliance')
def lista_compliance():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute("""
        SELECT sp.*, a.name as asset_name, c.function_name, c.category_name, c.description as control_desc
        FROM security_profile sp
        JOIN asset a ON sp.asset_id = a.asset_id
        JOIN acn_subcategory c ON sp.subcategory_code = c.code
        ORDER BY a.name, c.function_name, c.code
    """)
    profiles = cur.fetchall()
    conn.close()
    return render_template('compliance.html', profiles=profiles)

@app.route('/save_profile', methods=('GET', 'POST'))
@app.route('/save_profile/<string:id>', methods=('GET', 'POST'))
def save_profile(id=None):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    profile = None
    
    if id:
        cur.execute("SELECT * FROM security_profile WHERE profile_id = %s", (id,))
        profile = cur.fetchone()

    if request.method == 'POST':
        asset_id = request.form['asset_id']
        sub_code = request.form['subcategory_code']
        tier_current = request.form['implementation_tier_current']
        status = request.form['status_current']
        tier_target = request.form['implementation_tier_target']
        gap = request.form['gap_analysis']
        
        try:
            if id:
                cur.execute("""
                    UPDATE security_profile 
                    SET asset_id=%s, subcategory_code=%s, implementation_tier_current=%s, 
                        status_current=%s, implementation_tier_target=%s, gap_analysis=%s
                    WHERE profile_id=%s
                """, (asset_id, sub_code, tier_current, status, tier_target, gap, id))
                flash('Profilo di sicurezza aggiornato!', 'success')
            else:
                cur.execute("""
                    INSERT INTO security_profile (asset_id, subcategory_code, implementation_tier_current, status_current, implementation_tier_target, gap_analysis)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (asset_id, sub_code, tier_current, status, tier_target, gap))
                flash('Nuovo controllo ACN mappato sull\'asset!', 'success')
            conn.commit()
            return redirect(url_for('lista_compliance'))
        except Exception as e:
            conn.rollback()
            flash(f"Errore di salvataggio: {e}", 'danger')

    
    cur.execute("SELECT asset_id, name FROM asset ORDER BY name")
    assets = cur.fetchall()
    
    
    cur.execute("SELECT code, function_name, category_name FROM acn_subcategory ORDER BY function_name, code")
    acn_controls = cur.fetchall()
    
    conn.close()
    return render_template('form_profile.html', profile=profile, assets=assets, controls=acn_controls)

@app.route('/delete_profile/<string:id>')
def delete_profile(id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM security_profile WHERE profile_id = %s", (id,))
        conn.commit()
        flash('Profilo di compliance eliminato.', 'warning')
    except Exception as e:
        conn.rollback()
        flash(f"Errore: {e}", 'danger')
    conn.close()
    return redirect(url_for('lista_compliance'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)