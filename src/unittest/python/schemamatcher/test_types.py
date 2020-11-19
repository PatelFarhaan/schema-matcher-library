from schemamatcher.utils.types import infer_type, Type
import pandas as pd

class TestTypes():
    def test_infer_type(self):
        series = pd.Series([1, 2, 3, 4, 5, 6])
        itype = infer_type(series)
        assert (itype & Type.Numeric)
        ser = str(itype)
        itype = Type.deserialize(ser)
        assert (itype & Type.Numeric)
        series = pd.Series([
            'here is a sentence making this a long blob of text greater than 30 characters', 
            'and here is another sentence which is also a longish blob of text greater than 30 chars'])
        itype = infer_type(series)
        assert (itype & Type.Textual)
        ser = str(itype)
        itype = Type.deserialize(ser)
        assert (itype & Type.Textual)
        series = pd.Series(['a', 'b', 'b', 'c'])
        itype = infer_type(series, sample=True, sample_size=3)
        assert (itype & Type.Categorical)
        ser = str(itype)
        itype = Type.deserialize(ser)
        assert (itype & Type.Categorical)
        series = pd.Series(['2019-03-05', '2018-12-10'])
        itype = infer_type(series, sample=True, sample_size=3)
        assert (itype & Type.Datetime)
        ser = str(itype)
        itype = Type.deserialize(ser)
        assert (itype & Type.Datetime)
