# file mygame/typeclasses/latin_noun.py

from evennia import DefaultObject

class InflectedNoun(DefaultObject):
    """
    This is my solution to populating all of the inflected forms of
    Latin nouns on creation
    """

    def at_first_save(self):
        """
        This is called by the typeclass system whenever an instance of
        this class is saved for the first time. It is a generic hook
        for calling the startup hooks for the various game entities.
        When overloading you generally don't overload this but
        overload the hooks called by this method.

        """
        self.basetype_setup()
        # moving the below line to just before basetype_posthook
        # at the bottom of this defenitiion
        # self.at_object_creation()

        if hasattr(self, "_createdict"):
            # this will only be set if the utils.create function
            # was used to create the object. We want the create
            # call's kwargs to override the values set by hooks.
            cdict = self._createdict
            updates = []
            if not cdict.get("key"):
                if not self.db_key:
                    self.db_key = "#%i" % self.dbid
                    updates.append("db_key")
            elif self.key != cdict.get("key"):
                updates.append("db_key")
                self.db_key = cdict["key"]
            if cdict.get("location") and self.location != cdict["location"]:
                self.db_location = cdict["location"]
                updates.append("db_location")
            if cdict.get("home") and self.home != cdict["home"]:
                self.home = cdict["home"]
                updates.append("db_home")
            if cdict.get("destination") and self.destination != cdict["destination"]:
                self.destination = cdict["destination"]
                updates.append("db_destination")
            if updates:
                self.save(update_fields=updates)

            if cdict.get("permissions"):
                self.permissions.batch_add(*cdict["permissions"])
            if cdict.get("locks"):
                self.locks.add(cdict["locks"])
            if cdict.get("aliases"):
                self.aliases.batch_add(*cdict["aliases"])
            if cdict.get("location"):
                cdict["location"].at_object_receive(self, None)
                self.at_after_move(None)
            if cdict.get("tags"):
                # this should be a list of tags, tuples (key, category) or (key, category, data)
                self.tags.batch_add(*cdict["tags"])
            if cdict.get("attributes"):
                # this should be tuples (key, val, ...)
                self.attributes.batch_add(*cdict["attributes"])
            if cdict.get("nattributes"):
                # this should be a dict of nattrname:value
                for key, value in cdict["nattributes"]:
                    self.nattributes.add(key, value)

            del self._createdict

        self.at_object_creation()
        self.basetype_posthook_setup()
