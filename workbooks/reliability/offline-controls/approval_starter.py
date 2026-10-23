"""Independent checkpoint: finish this function before consulting approval_reference.py."""


def authorize(amount, approvers, current_operators):
    # TODO 1: reject non-integer/bool, nonpositive and >100 amounts.
    # TODO 2: require one distinct current operator, or two for amount >50.
    # TODO 3: deny if an approving operator has since been revoked.
    # Raise ValueError for invalid inputs, PermissionError for denied authority; return True otherwise.
    raise NotImplementedError('Implement trusted approval policy')


if __name__ == '__main__':
    try:
        authorize(60, ['sam', 'sam'], {'sam', 'lee'})
    except NotImplementedError:
        print('Starting checkpoint: policy not implemented; no approval granted.')
