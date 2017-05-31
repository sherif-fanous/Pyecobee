class EcobeeObject(object):
    def pretty_format(self, indent=2, level=0, sort_attributes=True):
        """
        Pretty format a response object

        :param indent: The amount of indentation added for each recursive level
        :param level: The recursion level
        :param sort_attributes: Whether to sort the attributes or not
        :return: six.text_type (This is unicode() in Python 2 and str in Python 3)
        """
        pretty_formatted = ['{0}(\n'.format(self.__class__.__name__)]
        level = level + 1
        for (i, attribute_name) in enumerate(sorted(self.__slots__) if sort_attributes else self.__slots__):
            if i:
                pretty_formatted.append(',\n')
            if isinstance(getattr(self, attribute_name), list):
                pretty_formatted.append('{0}{1}=[\n'.format(' ' * (indent * level),
                                                            self.attribute_name_map[attribute_name[1:]]))
                level = level + 1
                for (j, list_entry) in enumerate(getattr(self, attribute_name)):
                    if j:
                        pretty_formatted.append(',\n')
                    if hasattr(list_entry, 'pretty_format'):
                        pretty_formatted.append('{0}{1}'.format(' ' * (indent * level),
                                                                list_entry.pretty_format(indent,
                                                                                         level,
                                                                                         sort_attributes)))
                    else:
                        if isinstance(list_entry, list):
                            pretty_formatted.append('{0}[\n'.format(' ' * (indent * level)))
                            level = level + 1
                            for (k, sub_list_entry) in enumerate(list_entry):
                                if k:
                                    pretty_formatted.append(',\n')
                                pretty_formatted.append('{0}{1}'.format(' ' * (indent * level), sub_list_entry))
                            if list_entry:
                                pretty_formatted.append('\n')
                            level = level - 1
                            pretty_formatted.append('{0}]'.format(' ' * (indent * level)))
                        else:
                            pretty_formatted.append('{0}{1}'.format(' ' * (indent * level), list_entry))
                if getattr(self, attribute_name):
                    pretty_formatted.append('\n')
                level = level - 1
                pretty_formatted.append('{0}]'.format(' ' * (indent * level)))
            else:
                pretty_formatted.append(' ' * (indent * level))
                if hasattr(getattr(self, attribute_name), 'pretty_format'):
                    pretty_formatted.append('{0}={1!s}'.format(self.attribute_name_map[attribute_name[1:]],
                                                               getattr(self, attribute_name).pretty_format(
                                                                   indent,
                                                                   level,
                                                                   sort_attributes)))
                else:
                    pretty_formatted.append('{0}={1!s}'.format(self.attribute_name_map[attribute_name[1:]],
                                                               getattr(self, attribute_name)))
        level = level - 1
        pretty_formatted.append('\n{0})'.format(' ' * (indent * level)))
        return ''.join(pretty_formatted)

    def __repr__(self):
        return '{0}('.format(self.__class__.__name__) + ', '.join(
            ['{0}={1!r}'.format(attribute_name[1:], getattr(self, attribute_name)) for attribute_name in
             self.__slots__]) + ')'

    def __str__(self):
        return '{0}('.format(self.__class__.__name__) + ', '.join(
            ['{0}={1!s}'.format(type(self).attribute_name_map[attribute_name[1:]], getattr(self, attribute_name)) for
             attribute_name in self.__slots__]) + ')'
