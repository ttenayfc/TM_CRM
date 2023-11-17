# -*- coding: utf-8 -*-
import datetime

import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


# Tabla res.partner. Tiene adicionado los campos necesarios para la ficha del cliente en TM
class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Usar ref como codigo ver como le incorporo esta funcionalidad default='codigo_generado')
    # FC_fechaDia_numConsecutivo (automatico)
    ref = fields.Char(string='Código FC', index=True, default='codigo_generado', readonly=True)
    modelo_fc = fields.Char(string='Modelo', default="0077.A1 Rev.06")
    reeup = fields.Char(string='REEUP', size=11)
    carnet = fields.Char(string='CI', size=11)  # Carnet de identidad
    # usar vat que es el NIF y para Cuba es el NIT
    organismo_id = fields.Many2one('tm.organismo', string="Organismo", help="Organismo al que pertenece.")
    osde_id = fields.Many2one('tm.osde', string='OSDE', help="Organización Superior de Dirección Empresarial.")
    no_estatal = fields.Selection(string='No Estatal', help="Seleccione tipo de forma de gestion no estatal.",
                                  selection=[
                                      ('mipyme', 'MiPyme'),
                                      ('ees', 'Empresa Estatal Socialista'),
                                      ('ueb_ees', 'UEB Empresa Estatal Socialista'),
                                      ('tcp', 'Trabajador Cuenta Propia'),
                                      ('cna', 'Cooperativa no agropecuaria'),
                                      ('cpa', 'Cooperativa produccion agropecuaria'),
                                      ('ofgne', 'Otra forma de gestion no estatal')
                                  ])
    nuevocli = fields.Boolean(string='Nuevo cliente', help="Marque si es nuevo cliente.")
    cliente = fields.Boolean(string='Cliente', default=True, help="Marque si es cliente.")
    cli_potencial = fields.Boolean(string='Cliente potencial', help="Marque si es cliente potencial.")
    proveedor = fields.Boolean(string='Proveedor', help="Marque si es proveedor.")
    prov_potencial = fields.Boolean(string='Proveedor potencial', help="Marque si es proveedor potencial.")
    # Empresa o forma gestion no estatal (EFGNE)
    efgne_id = fields.Many2one('tm.efgne', string="Empresa o forma de gestión no estatal")
    uebda_id = fields.Many2one('tm.uebda', string="UEB o Dependencia autorizada",
                               help="Seleccione la Unidad Empresarial de Base(UEB) o dependencia autorizada.")
    encuesta = fields.Selection(required=True, selection=[
        ('reconocimiento_nac', 'Reconocimiento nacional'),
        ('organismo_superior', 'Organismo Superior'),
        ('ferias_evento', 'Ferias y eventos'),
        ('promociones_tm', 'Promociones de TM'),
        ('redes_sociales', 'Redes sociales'),
        ('otra_empresa_persona', 'Otra empresa o persona'),
        ('cli_historico', 'Cliente histórico'),
        ('otra_via', 'Otra vía')
    ])
    firma = fields.Binary(string="Firma")
    cunno = fields.Binary(string="Cuño")

    @api.constrains('reeup', 'carnet', 'vat')
    def _check(self):
        for record in self:
            if record.reeup and (not record.reeup.isdigit() or len(record.reeup) < 5 or len(record.reeup) > 11):
                raise ValidationError("El campo 'REEUP' debe tener entre 5 y 11 caracteres y solo números.")
            if record.carnet and (not record.carnet.isdigit() or len(record.carnet) != 11):
                raise ValidationError("El campo 'Carnet' debe tener 11 caracteres y solo números.")
            if record.vat and (not record.vat.isdigit() or len(record.vat) != 11):
                raise ValidationError(
                    "El campo 'NIT (Número de identificación tributaria)' debe tener 11 caracteres y solo números.")

    def codigo_generado(self):
        # Pasos: 1. Obtener el ultimo cliente en base de datos
        # 2. Extraer el anno y comparar con el actual
        # 3. Si son iguales: estraer el número consecutivo del cliente y sumarle 1/ No son iguales: inicializar el
        # consecutivo en 1
        fecha = fields.datetime.date.today()
        # Generar el número consecutivo basado en registros existentes
        last_record = self.search([], order='id desc', limit=1)
        if last_record:
            last_number = int(last_record.field.split('-')[-1])
            return f'FC-{fields.Date.today().strftime("%d%m%Y")}-{last_number + 1}'
        else:
            return f'FC-{fields.Date.today().strftime("%d%m%Y")}-1'


# Contacto del cliente
class Partner(models.Model):
    _inherit = 'res.partner'

    carnet = fields.Char(string='CI', size=11)  # Carnet de identidad
    firma = fields.Binary(string="Firma")

    @api.constrains('carnet')
    def _check(self):
        for record in self:
            if record.carnet and (not record.carnet.isdigit() or len(record.carnet) != 11):
                raise ValidationError("El campo 'Carnet' debe tener 11 caracteres y solo números.")


class PartnerProveedor(models.Model):
    _name = 'tm.contacto_proveedor'
    _description = 'Contactos de un proveedor '

    name = fields.Char(index=True, default_export_compatible=True, string='Nombre', placeholder='Nombre y apellidos')
    title = fields.Many2one('res.partner.title', string='Cargo')
    country_id = fields.Many2one('res.country', string='País', ondelete='restrict')
    phone = fields.Char(unaccent=False, string='Teléfono')
    mobile = fields.Char(unaccent=False, string='Celular')
    email = fields.Char(string='Correo electrónico')
    tipo_contacto = fields.Many2many('tm.tipo_contacto', relation='tm_contacto_tipo_rel', column1='contacto_id',
                                   column2='tipo_id', string='Tipo de contacto')

    @api.constrains('name', 'phone', 'mobile')
    def _check(self):
        for record in self:
            if record.name and not record.name.replace(' ', '').isalpha():
                raise ValidationError("El campo 'Nombre' solo puede contener caracteres.")
            if record.phone and not record.phone.replace(' ', '').replace('+', '').replace('-', '').isdigit():
                raise ValidationError("El campo 'Teléfono' solo puede contener números.")
            if record.mobile and not record.mobile.replace(' ', '').replace('+', '').replace('-', '').isdigit():
                raise ValidationError("El campo 'Celular' solo puede contener números.")


class TMProveedor(models.Model):
    # _inherit = 'res.partner'
    _name = 'tm.proveedor'
    _description = 'Ficha proveedor TM'

    modelo_fp = fields.Char(string='Modelo', default="0076AA1-l")
    fecha_mod = fields.Date(string='Fecha actualización', default=datetime.date.today())
    cliente = fields.Boolean(string='Cliente', help="Marque si es cliente.")
    proveedor = fields.Boolean(string='Proveedor', help="Marque si es proveedor.")
    name = fields.Char(string='Nombre compañía', required=True)
    siglas = fields.Char(string='Siglas')
    ref = fields.Char(string='Código MINCEX', index=True, size=11, required=True)
    street = fields.Char(string='Domicilio legal')
    city = fields.Char(string='Ciudad')
    state = fields.Char(string='Distrito')
    country_id = fields.Many2one('res.country', string='País')
    zip = fields.Char(string='Código postal')
    phone = fields.Char(string='Teléfono')
    fax = fields.Char(string='Fax')
    email = fields.Char(string='Correo electrónico')
    website = fields.Char(string='Sitio web')
    fecha_fundacion = fields.Date(string='Fecha fundación')
    no_empleados = fields.Integer(string='No. empleados')
    capital = fields.Float(string='Capital monetario')
    moneda_id = fields.Many2one('res.currency', string='Moneda')
    tematica_id = fields.Many2many('tm.tematica', relation='tm_proveedor_tema_rel', column1='proveedor_id',
                                   column2='tematica_id', string='Temática')
    bank_ids = fields.One2many('res.partner.bank', 'proveedor_id', string='Cuentas bancarias')
    child_ids = fields.Many2many('tm.contacto_proveedor', relation='tm_proveedor_contact_rel', column1='proveedor_id',
                                 column2='contacto_id', string="Contacto")
    sucursal_id = fields.Many2one('tm.sucursal', string='Sucursal')
    casa_matriz = fields.Char(string='Casa matriz')
    productos = fields.Text(string='Productos que comercializa')
    actividad_id = fields.Many2many('tm.actividad', 'tm_proveedor_actividad_rel', column1='proveedor_id',
                                    column2='actividad_id', string='Actividad')
    paises_comercializa = fields.Many2many('res.country', 'tm_proveedor_pais_rel', column1='proveedor_id',
                                           column2='pais_id', string='Pais(es) con el(los) que se relaciona(n)')
    emp_cub_rel = fields.Text(
        string='Empresas cubanas con las que se relacionan')  # empresas cubanas con las que se relaciona
    valoracion = fields.Text(string='Valoración del desempeño')

    @api.constrains('name', 'siglas', 'phone', 'email', 'fecha_fundacion')
    def _check(self):
        for record in self:
            if record.name and not record.name.replace(' ', '').isalpha():
                raise ValidationError("El campo 'Nombre de la compañia' solo puede contener caracteres.")
            if record.siglas and not record.siglas.replace(' ', '').isalpha():
                raise ValidationError("El campo 'Siglas' solo puede contener caracteres.")
            if record.phone and not record.phone.replace(' ', '').replace('+', '').replace('-', '').isdigit():
                raise ValidationError("El campo 'Teléfono' solo puede contener números.")
            if record.email and not re.match(r"[^@]+@[^@]+\.[^@]+", record.email):
                raise ValidationError('El campo de correo electrónico no tiene un formato válido.')
            if record.fecha_fundacion and record.fecha_fundacion > date.today():
                raise ValidationError("Solo se acepta como mínimo para la 'Fecha fundación' la fecha actual.")


class TMSucursal(models.Model):
    _inherit = 'tm.datos'
    _name = 'tm.sucursal'
    _description = 'Datos de sucursal en Cuba para los proveedores internacionales.'

    name = fields.Char(string='Sucursal', help="Escriba el nombre.")
    fax = fields.Char(string='Fax')
    sucursal_cuba = fields.Selection(string='Sucursal en Cuba', help="Seleccione si tiene sucursal.",
                                     selection=[('si', 'Sí'), ('no', 'No')], default=False)
    no_licencia = fields.Char(string='No. Licencia Cámara Comercio Cuba', required=True, help="Número obligatorio")

    @api.constrains('name')
    def _check(self):
        for record in self:
            if record.name and not record.name.replace(' ', '').isalpha():
                raise ValidationError("El campo 'Nombre' solo puede contener caracteres.")
            if record.fax and not record.fax.replace(' ', '').replace('+', '').replace('-', '').isdigit():
                raise ValidationError("El campo 'Fax' solo puede contener números.")


class TMTematica(models.Model):
    _name = "tm.tematica"
    _description = "Tematicas de los proveedores internacionales."

    name = fields.Char(string='Temática(s)')

    @api.constrains('name')
    def _check(self):
        for record in self:
            if record.name and not record.name.replace(' ', '').isalpha():
                raise ValidationError("El campo 'Temática(s)' solo puede contener caracteres.")


class TMActividad(models.Model):
    _inherit = 'res.partner.category'
    _name = 'tm.actividad'
    _description = "Actividades."

    name = fields.Char(string='Actividad', required=True)

    @api.constrains('name')
    def _check(self):
        for record in self:
            if record.name and not record.name.replace(' ', '').isalpha():
                raise ValidationError("El campo 'Actividad' solo puede contener caracteres.")


# Tipos de contactos para los proveedores internacionales
# (Accionista /Junta Directiva /Contacto extranjero /Contacto Cuba)
class TMTipoContacto(models.Model):
    _name = 'tm.tipo_contacto'
    _description = "Tipos de contactos."

    name = fields.Char(string='Tipo contacto', required=True)

    @api.constrains('name')
    def _check(self):
        for record in self:
            if record.name and not record.name.replace(' ', '').isalpha():
                raise ValidationError("El campo 'Tipo contacto' solo puede contener caracteres.")
