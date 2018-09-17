#!/usr/bin/python

import tempfile
import errno
import os
import tarfile

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: psadeploy

short_description: This is my sample module

version_added: "2.4"

description:
    - "This is my longer description explaining my sample module"

options:
    name:
        description:
            - This is the message to send to the sample module
        required: true
    new:
        description:
            - Control to demo if the result of this module is changed or not
        required: false

author:
    - Your Name (@yourhandle)
'''

EXAMPLES = '''
# Pass in a message
- name: Test with a message
  my_new_test_module:
    name: hello world

# pass in a message and have changed true
- name: Test with a message and changed output
  my_new_test_module:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  my_new_test_module:
    name: fail me
'''

RETURN = '''
tarball:
    description: Path to the tarball in dest folder
    type: str
deploy_successful:
    description: Whether the module succeeded or not
    type: bool
'''

from ansible.module_utils.basic import AnsibleModule

def run_module():
    # Definicion de los argumentos que se nos pueden pasar
    module_args = dict(
        name=dict(type='str', required=True),
        path=dict(type='str', required=True),
        dest=dict(type='str', required=False),
        version=dict(type='str', required=False, default="1.0")
        #new=dict(type='bool', required=False, default=False)
    )
    #Diccionario con los resultados. De momento: fallo y sin path
    result = dict(
        changed=False,
        tarball='',
        success=False
    )

    # Instanciamos el objeto "AnsibleModule", que es nuestra abstraccion
    # de la llamada a ansible. Aqui indicamos el array de los argumentos 
    # esperados y si soportamos el check_mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    
    # Cosas a hacer si estamos en check mode
    if module.check_mode:
        module.exit_json(**result)

    # Debug
    # import pdb; pdb.set_trace()

    # Cosas a hacer si no estamos en check mode
  
    # Definimos el directorio de destino, por defecto en /tmp
    dest='/tmp/'
    if len(module.params['dest']) > 0:
        dest=module.params['dest']

    # Comprobaremos que dest es escribible 
    try: 
       testfile=tempfile.TemporaryFile(dir = dest)
       testfile.close()   
    except OSError as e:
       if e.errno == errno.EACCES:  # 13
           errormsg='El directorio destino='+dest+' no es escribible'
           module.fail_json(msg=errormsg, **result)
       else:
           errormsg='Hay problemas entrando en el directorio destino='+dest
           module.fail_json(msg=errormsg, **result)

    if len(module.params['version'])>0:
        version="-"+module.params['version']
    else:
        version=""
    
    if dest[len(dest)-1]=='/':
        tarball=dest+module.params['name']+version+".tar.gz"
    else:
        tarball=dest+"/"+module.params['name']+version+".tar.gz"

    try: 
       with tarfile.open(tarball,"w:gz") as tar_handle:
          for root, dirs, files in os.walk(module.params['path']):
             for file in files: 
                 tar_handle.add(os.path.join(root,file))
    except Exception as e:
       module.fail_json(msg=e.message, **result)

    result['tarball'] =  tarball
    result['changed'] = True
    result['success'] = True
    result['deploy_successful'] = True
    
    # Si algo va mal, ejecutamos AnsibleModule.fail_json() para pasar 
    # el mensaje de error y el resultado
    if module.params['name'] == 'destroyworld':
        module.fail_json(msg='Algo no fue bien...', **result)

    # Si todo va bien, llamamos a exit_json con el resultado
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
