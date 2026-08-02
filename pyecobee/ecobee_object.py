from itertools import chain


class EcobeeObject:
    __slots__ = []

    attribute_name_map = {}

    attribute_type_map = {}

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            + ", ".join(
                [
                    f"{attribute_name[1:]}={getattr(self, attribute_name)!r}"
                    for attribute_name in self.slots()
                ]
            )
            + ")"
        )

    def __str__(self):
        return (
            f"{self.__class__.__name__}("
            + ", ".join(
                [
                    f"{type(self).attribute_name_map[attribute_name[1:]]}={getattr(self, attribute_name)!s}"
                    for attribute_name in self.slots()
                ]
            )
            + ")"
        )

    def pretty_format(self, indent=2, level=0, sort_attributes=True):
        """
        Pretty format a response object

        :param indent: The amount of indentation added for each
        recursive level
        :param level: The recursion level
        :param sort_attributes: Whether to sort the attributes or not
        :return: str
        """
        pretty_formatted = [f"{self.__class__.__name__}(\n"]
        level = level + 1

        for i, attribute_name in enumerate(
            sorted(self.slots()) if sort_attributes else self.slots()
        ):
            if i:
                pretty_formatted.append(",\n")

            if isinstance(getattr(self, attribute_name), list):
                pretty_formatted.append(
                    "{}{}=[\n".format(
                        " " * (indent * level),
                        self.attribute_name_map[attribute_name[1:]],
                    )
                )
                level = level + 1

                for j, list_entry in enumerate(getattr(self, attribute_name)):
                    if j:
                        pretty_formatted.append(",\n")

                    if hasattr(list_entry, "pretty_format"):
                        pretty_formatted.append(
                            "{}{}".format(
                                " " * (indent * level),
                                list_entry.pretty_format(
                                    indent, level, sort_attributes
                                ),
                            )
                        )
                    else:
                        if isinstance(list_entry, list):
                            pretty_formatted.append(
                                "{}[\n".format(" " * (indent * level))
                            )

                            level = level + 1

                            for k, sub_list_entry in enumerate(list_entry):
                                if k:
                                    pretty_formatted.append(",\n")

                                pretty_formatted.append(
                                    "{}{}".format(
                                        " " * (indent * level), sub_list_entry
                                    )
                                )

                            if list_entry:
                                pretty_formatted.append("\n")

                            level = level - 1
                            pretty_formatted.append(
                                "{}]".format(" " * (indent * level))
                            )
                        else:
                            pretty_formatted.append(
                                "{}{}".format(" " * (indent * level), list_entry)
                            )

                if getattr(self, attribute_name):
                    pretty_formatted.append("\n")

                level = level - 1
                pretty_formatted.append("{}]".format(" " * (indent * level)))
            else:
                pretty_formatted.append(" " * (indent * level))

                if hasattr(getattr(self, attribute_name), "pretty_format"):
                    pretty_formatted.append(
                        "{}={!s}".format(
                            self.attribute_name_map[attribute_name[1:]],
                            getattr(self, attribute_name).pretty_format(
                                indent, level, sort_attributes
                            ),
                        )
                    )
                else:
                    pretty_formatted.append(
                        f"{self.attribute_name_map[attribute_name[1:]]}={getattr(self, attribute_name)!s}"
                    )

        level = level - 1
        pretty_formatted.append("\n{})".format(" " * (indent * level)))

        return "".join(pretty_formatted)

    def slots(self):
        return chain.from_iterable(
            getattr(cls, "__slots__", []) for cls in type(self).__mro__
        )
