from .stats.StatResult import StatResult
from .stats.utils import return_results
from typing import Union, List
import numpy as np
import pandas as pd


def pval_annotation_text(
    result: Union[List[StatResult], StatResult], pvalue_thresholds
):
    p_values = np.array([res.pval for res in np.atleast_1d(result)])
    significance_suffixes = [
        res.significance_suffix for res in np.atleast_1d(result)
    ]

    significance_annotations = pd.Series(["" for _ in range(len(p_values))])
    pvalue_thresholds = (
        pd.DataFrame(pvalue_thresholds)
        .sort_values(by=0, ascending=False)
        .values
    )
    last_p_upper_bound = 1.1
    for i in range(0, len(pvalue_thresholds)):
        p_upper_bound = pvalue_thresholds[i][0]
        assert (
            p_upper_bound < last_p_upper_bound
        ), 'pvalue_thresholds are not monotonically decreasing'
        significance_str = pvalue_thresholds[i][1]

        # Assign the significance label to p-values below upper bound.
        # Note: if the p-value is also below the next threshold, this will get
        # overwritten.
        significance_annotations[p_values <= p_upper_bound] = significance_str

        last_p_upper_bound = p_upper_bound

    significance_annotations_with_suffixes = [
        f"{star}{signif}"
        for star, signif in zip(
            significance_annotations, significance_suffixes
        )
    ]

    return return_results(significance_annotations_with_suffixes)

def simple_text(result: StatResult, pvalue_format, pvalue_thresholds, test_short_name=None):
    """
    Generates simple text for test name and pvalue
    :param result: StatResult instance
    :param pvalue_format: format string for pvalue
    :param test_short_name: Short name of test to show
    :param pvalue_thresholds: String to display per pvalue range
    :return: simple annotation
    """
    # Sort thresholds
    thresholds = sorted(pvalue_thresholds, key=lambda x: x[0])

    # Test name if passed
    text = test_short_name and test_short_name + " " or ""

    for threshold in thresholds:
        if result.pval < threshold[0]:
            pval_text = "p ≤ {}".format(threshold[1])
            break
    else:
        pval_text = "p = {}".format(pvalue_format).format(result.pval)

    return text + pval_text + result.significance_suffix
