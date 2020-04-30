from flask import render_template, url_for,Blueprint
from flask import current_app as app
from app.models import db,Plants,Countries,Inverters,Inverter_Mans,Meters,Meter_Mans,IPs,Grid_Codes
import sqlalchemy.orm as sqlorm

main_bp = Blueprint('main_bp', __name__,
                    template_folder='templates',
                    static_folder='static')


@main_bp.route('/')
@main_bp.route('/index')
def index():
    user = {'username': 'Spiros'}
    plants_count = len(Plants.query.all())
    ppc_count = Plants.query.filter(Plants.ppc_ip_id != 1).count()
    ppc_countries_count = Plants.query.filter(Plants.ppc_ip_id!=1).with_entities(Plants.country_id).distinct().count()
    countries = Plants.query.with_entities(Plants.country_id).distinct().count()
    m=sqlorm.aliased(Meters)
    result =  db.session.query(Plants,Countries,Inverters,Meters,IPs,Grid_Codes,m).join(Countries,Plants.country_id==Countries.id).join(Inverters,Plants.inverter_id==Inverters.id).join(Meters,Plants.ppc_meter_id==Meters.id)\
    .join(IPs,Plants.ppc_ip_id==IPs.id).join(Grid_Codes,Plants.grid_code_id==Grid_Codes.id).join(m,Plants.pcc_meter_id==m.id).all()
    return render_template('index.html', title='Home',user=user,plants=result,ppc_count=ppc_count,
                ppc_countries_count=ppc_countries_count,plants_count=plants_count,countries=countries)

@main_bp.route('/inverters')
def inverters():
    inverter_count = len(Inverters.query.all())
    inverter_man_count = len(Inverter_Mans.query.all())
    result = db.session.query(Inverters,Inverter_Mans).join(Inverter_Mans,Inverters.man_id==Inverter_Mans.id).all()
    return render_template('inverters.html',title="Inverters",inverters=result,inv_count=inverter_count,man_count=inverter_man_count)

@main_bp.route('/inverters/manufacturers')
def inv_mans():
    # inverter_count = len(Inverters.query.all())
    # inverter_man_count = len(Inverter_Mans.query.all())
    result = db.session.query(Inverter_Mans).all()
    inv_mans = [man.manufacturer for man in result]
    inv_mans.sort()
    return render_template('lists.html',title="Inverter Manufacturers",_list=inv_mans)


@main_bp.route('/meters')
def meters():
    meter_count = len(Meters.query.all())
    meter_man_count = len(Meter_Mans.query.all())
    result = db.session.query(Meters,Meter_Mans).join(Meter_Mans,Meters.man_id==Meter_Mans.id).all()
    return render_template('meters.html',title="Meters",meters=result,meter_count=meter_count,man_count=meter_man_count)

@main_bp.route('/meters/manufacturers')
def meter_mans():
    # inverter_count = len(Inverters.query.all())
    # inverter_man_count = len(Inverter_Mans.query.all())
    result = db.session.query(Meter_Mans).all()
    meter_mans = [man.manufacturer for man in result]
    meter_mans.sort()
    return render_template('lists.html',title="Meter Manufacturers",_list=meter_mans)

@main_bp.route('/countries')
def countries():
    # meter_count = len(Countries.query.all())
    # meter_man_count = len(Meter_Mans.query.all())
    result = db.session.query(Countries).all()
    countries= [c.country for c in result]
    countries.sort()
    # print(countries)
    return render_template('lists.html',title="Countries",_list=countries)


@main_bp.route('/index/<slug>')
def details(slug):
    print("This is the fucking " + slug)
    m=sqlorm.aliased(Meters)
    plant =  db.session.query(Plants,Countries,Inverters,Meters,IPs,Grid_Codes,m).join(Countries,Plants.country_id==Countries.id).join(Inverters,Plants.inverter_id==Inverters.id).join(Meters,Plants.ppc_meter_id==Meters.id)\
        .join(IPs,Plants.ppc_ip_id==IPs.id).join(Grid_Codes,Plants.grid_code_id==Grid_Codes.id).join(m,Plants.pcc_meter_id==m.id).filter(Plants.plant==slug).first()
    plant_ips=IPs.query.filter_by(plant_id=plant[0].id).all()
    plant_ips=[ip for ip in plant_ips if ip.ip!='-']
    return render_template('details.html',title="Plants-Details",plant=plant,ips=plant_ips)
