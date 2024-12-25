account_filters_data = [
  {
    "name": "account_name",
    "slug": "account_name",
    "selected": False,
    "value": "",
    "type": "text"
  },
  {
    "name": "account_number",
    "slug": "account_id",
    "selected": False,
    "value": "",
    "type": "text"
  },
  {
    "name": "HQ Account Name",
    "slug": "parent_account__account_name",
    "selected": False,
    "value": "",
    "type": "text"
  },
  {
    "name": "HQ Account Number",
    "slug": "parent_account__account_id",
    "selected": False,
    "value": "",
    "type": "text"
  },
  {
    "name": "account_type",
    "slug": "account_type",
    "selected": False,
    "value": None,
    "type": "select",
    "options": [
      {
        "name": "Subsidiary",
        "value": "sub"
      },
      {
        "name": "HQ",
        "value": "hq"
      },
      {
        "name": "HQ/Subsidiary",
        "value": "hq_sub"
      }
    ]
  },
  {
    "name": "account_admin",
    "slug": "users__name",
    "selected": False,
    "value": "",
    "type": "text"
  },
  {
    "name": "city",
    "slug": "city",
    "selected": False,
    "value": "",
    "type": "text"
  },
  {
    "name": "state",
    "slug": "state",
    "selected": False,
    "value": "",
    "type": "text"
  },
  {
    "name": "address",
    "slug": "address1",
    "selected": False,
    "value": "",
    "type": "text"
  },
  {
    "name": "active",
    "slug": "is_active",
    "selected": False,
    "value": None,
    "type": "select",
    "options": [
      {
        "name": "Active",
        "value": True
      },
      {
        "name": "Inactive",
        "value": False
      }
    ]
  }
]

case_filters_data = [
  {
    "name": "case_number",
    "slug": "case_no",
    "selected": False,
    "value": "",
    "type": "text"
  },
  {
    "name": "account_name",
    "slug": "account__account_name",
    "selected": False,
    "value": "",
    "type": "text"
  },
  {
    "name": "devices_serial_number",
    "slug": "current_device",
    "selected": False,
    "value": "",
    "type": "text"
  },
  {
    "name": "Case Manager",
    "slug": "case_manager_name",
    "selected": False,
    "value": "",
    "type": "text"
  },
  {
    "name": "status",
    "slug": "is_active",
    "selected": False,
    "value": "",
    "type": "select",
    "apiUrl": "/api/web/cases/statuses",
    "bindLabel": "name",
    "bindValue": "value",
    "searchColumn": "name"
  },
  {
    "name": "is_archived",
    "slug": "is_archived",
    "selected": False,
    "value": "",
    "type": "select",
    "apiUrl": "/api/web/cases/archive_choices",
    "bindLabel": "name",
    "bindValue": "value",
    "searchColumn": "name"
  },
  {
    "name": "account_number",
    "slug": "account__account_id",
    "selected": False,
    "value": "",
    "type": "text"
  },
  {
    "name": "patient_name",
    "slug": "patient__slug",
    "selected": False,
    "value": "",
    "type": "text"
  },
  {
    "name": "parent_name",
    "slug": "parent_user__name",
    "selected": False,
    "value": "",
    "type": "text"
  },
  {
    "name": "scorer",
    "slug": "scorer_name",
    "selected": False,
    "value": "",
    "type": "text"
  },
  {
    "name": "interpreting_physician",
    "slug": "interpreting_physician_name",
    "selected": False,
    "value": "",
    "type": "text"
  },
  {
    "name": "medical_record",
    "slug": "patient__medical_record",
    "selected": False,
    "value": "",
    "type": "text"
  }
]

user_filters_data = [
  {
    "name": "Name",
    "slug": "name",
    "selected": False,
    "value": "",
    "type": "text"
  },
  {
    "name": "Email",
    "slug": "email",
    "selected": False,
    "value": "",
    "type": "text"
  },
  {
    "name": "Phone",
    "slug": "phone",
    "selected": False,
    "value": "",
    "type": "text"
  },
  {
    "name": "account_number",
    "slug": "account__account_id",
    "selected": False,
    "value": "",
    "type": "text"
  },
  {
    "name": "account_name",
    "slug": "account__account_name",
    "selected": False,
    "value": "",
    "type": "text"
  },
  {
    "name": "HQ Account Number",
    "slug": "account__parent_account__account_id",
    "selected": False,
    "value": "",
    "type": "text"
  },
  {
    "name": "User Type",
    "slug": "user_type",
    "selected": False,
    "value": "",
    "type": "select",
    "bindLabel": "name",
    "bindValue": "value",
    "apiUrl": "/api/web/users/user_types",
    "searchColumn": "name"
  },
  {
    "name": "City",
    "slug": "city",
    "selected": False,
    "value": "",
    "type": "text"
  },
  {
    "name": "State",
    "slug": "state",
    "selected": False,
    "value": "",
    "type": "text"
  },
  {
    "name": "status",
    "slug": "is_active",
    "selected": False,
    "value": "",
    "type": "select",
    "bindLabel": "name",
    "bindValue": "value",
    "apiUrl": "/api/web/users/statuses",
    "searchColumn": "name"
  }
]

device_filters_data = [
  {
    "name": "serial_number",
    "slug": "serial_number",
    "selected": False,
    "value": "",
    "type": "text",
    "apiUrl": "/api/web/devices/lookups/",
    "bindLabel": "serial_number",
    "bindValue": "slug",
    "searchColumn": "serial_number"
  },
  {
    "name": "account_name",
    "slug": "account__account_name",
    "selected": False,
    "value": "",
    "type": "select",
    "apiUrl": "/api/web/accounts/lookups/",
    "bindLabel": "account_name",
    "bindValue": 'account_name',
    "searchColumn": 'slug',
  },
  {
    "name": "item_number",
    "slug": "item__item_number",
    "selected": False,
    "value": "",
    "type": "select",
    "apiUrl": "/api/web/deviceItems/",
    "bindLabel": "item_number",
    "bindValue": "slug",
    "searchColumn": "slug"
  },
  {
    "name": "status",
    "slug": "is_active",
    "selected": False,
    "value": "",
    "type": "select",
    "options": [],
    "apiUrl": "/api/web/devices/statuses",
    "bindLabel": "name",
    "bindValue": "value",
    "searchColumn": "name"
  },
  {
    "name": "device_configuration",
    "slug": "item__configuration",
    "selected": False,
    "value": "",
    "type": "select",
    "apiUrl": "/api/web/deviceItems/",
    "bindLabel": "configuration",
    "bindValue": "configuration",
    "searchColumn": "configuration"
  },
  {
    "name": "device_enabled",
    "slug": "device_enabled",
    "selected": False,
    "value": "",
    "type": "select",
    "apiUrl": '/api/web/devices/device_enabled_choices/',
    "bindLabel": "name",
    "bindValue": "value",
    "searchColumn": "name"
  }
]