from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager

if __name__ == '__main__':
    inventory_file_name = 'inventory/hosts'
    data_loader = DataLoader()
    inventory = InventoryManager(loader = data_loader,
                             sources=[inventory_file_name])

    print(inventory.get_groups_dict()['mongod1'])