def separate_by_digit(contracts):
        """
        Method to separate contract information into types and
        durations ('Stage(4 à 6 mois)' ---> 'Stage' AND '4 à 6 mois')
        """
        contract_types = []
        contract_durations = []

        for string in contracts:
            index_digit = next((i for i, c in enumerate(string) if c.isdigit()), None)

            if index_digit is not None:
                contract_types.append(string[:index_digit - 1])
                contract_durations.append(string[index_digit:-1])
            else:
                contract_types.append(string)
                contract_durations.append("Undetermined")

        return contract_types, contract_durations
