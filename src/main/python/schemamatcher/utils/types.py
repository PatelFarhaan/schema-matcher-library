import enum


class Type(enum.Flag):
    String = 1
    Numeric = 1 << 1
    Categorical = 1 << 2
    Textual = 1 << 3
    Datetime = 1 << 4

    @staticmethod
    def deserialize(string):
        s = string.replace('Type.', '')
        types = s.split('|')
        itype = Type.String
        for type in types:
            if type == 'Textual':
                itype = itype | Type.Textual
            elif type == 'Categorical':
                itype = itype | Type.Categorical
            elif type == 'Numeric':
                itype = itype | Type.Numeric
            elif type == 'Datetime':
                itype = itype | Type.Datetime
        return itype


def infer_type(series, sample=False, sample_size=1000, text_length=30, random_state=1):
    """
    Infers the type of the input series
    :param series: pandas series whose type needs to be inferred
    :param sample: boolean whether to sample the series or not
    :param sample_size: int specifying the sample size
    :param text_length: average length
    :param random_state: initial random state for
    :return: enum indicating the inferred type
    """
    series = series[series.notnull()]
    inferred_type = Type.String

    if sample and len(series) > sample_size:
        series = series.sample(sample_size, random_state=random_state)

    if series.dtype == 'int64' or series.dtype == 'float64':
        inferred_type = inferred_type | Type.Numeric

    # Need a good datetime re pattern instead of the following
    try:
        if series.dtype == 'object' and series.str.match(r'\d{4}-\d{2}-\d{2}').sum() == len(series):
            inferred_type = inferred_type | Type.Datetime
        elif series.dtype == 'object' and series.str.match(r'\d{1,2}/\d{1,2}/\d{4}').sum() == len(series):
            inferred_type = inferred_type | Type.Datetime
    except AttributeError:
        pass

    if series.astype(str).apply(lambda x: len(x)).mean() > text_length:
        inferred_type = inferred_type | Type.Textual

    if len(series.unique()) < 5:
        inferred_type = inferred_type | Type.Categorical

    return inferred_type
