import json
import shutil
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible import context
import ansible.constants as C

context.CLIARGS = ImmutableDict(connection='smart', module_path=[''], forks=10, become=None,
                                become_method=None, become_user=None, check=False, diff=False, verbosity=5)

loader = DataLoader() 
inventory = InventoryManager(loader=loader, sources='www.app.com, ')
variable_manager = VariableManager(loader=loader, inventory=inventory)
passwords = dict()

play_source =  dict(
        name = "Playbook to check connectivity and print memory stats",
        hosts = 'www.app.com',
        gather_facts = 'no',
        tasks = [
            # task to check the connectivity with ping
            dict(action=dict(module='ping', args='')),
            # Task to get the memory stats
            dict(action=dict(module='shell', args='free -m'), register='output'),
            dict(action=dict(module='debug', args=dict(msg='{{output.stdout}}')))
         ]
    )

play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

tqm = None
try:
    tqm = TaskQueueManager(
              inventory=inventory,
              variable_manager=variable_manager,
              loader=loader,
              passwords=passwords,
          )
    result = tqm.run(play) 
finally:
    if tqm is not None:
        tqm.cleanup()

    shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)
