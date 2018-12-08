"""
This is the example to show how to use theoLibrary.
By the execution of this file, it is easy to understand how to work and how to use theoLibrary.
"""

if __name__ == "__main__":
    from src.System import system
    from comp.MongoDBCtrl import MongoDBCtrl

    system.register_component('MongoDBCtrl', MongoDBCtrl)
    system.startup_components()

    system.start_admin_prompt()
