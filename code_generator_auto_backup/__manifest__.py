{
    'name': 'Code Generator Auto Backup',
    'version': '12.0.1.0',
    'author': 'TechnoLibre',
    'website': 'https://technolibre.ca',
    'license': 'AGPL-3',
    'application': True,
    'depends': [
        'code_generator',
        'code_generator_cron',
    ],
    'installable': True,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
