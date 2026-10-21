"""Fitting heavy-tailed distributions."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import special


@dataclass(frozen=True)
class PowerLawFit:
    """Result of :func:`fit_power_law`.

    ``alpha`` and its standard error, the lower cut-off ``xmin``, the number of
    points in the fitted tail, the KS distance of the fit, and the comparison with
    an exponential tail: ``loglik_ratio`` > 0 favours the power law, < 0 the
    exponential; ``p_value`` says whether that sign is significant.
    """

    alpha: float
    alpha_err: float
    xmin: int
    n_tail: int
    ks: float
    loglik_ratio: float
    p_value: float


def _alpha_mle(tail: np.ndarray, xmin: int) -> float:
    # Discrete approximation from Clauset, Shalizi & Newman (2009), eq. 3.7.
    return 1.0 + len(tail) / np.sum(np.log(tail / (xmin - 0.5)))


def _ks_distance(tail: np.ndarray, alpha: float, xmin: int) -> float:
    values = np.unique(tail)
    empirical = np.searchsorted(np.sort(tail), values, side="right") / len(tail)
    model = 1.0 - special.zeta(alpha, values + 1) / special.zeta(alpha, xmin)
    return float(np.max(np.abs(empirical - model)))


def fit_power_law(data: np.ndarray, min_tail: int = 50) -> PowerLawFit:
    """把离散数据的尾部拟合成幂律 p(x) ∝ x^(−α)，并和指数尾部比较哪个更好。

    做什么
        对每个候选下界 ``xmin``（数据里出现过、且尾部至少 ``min_tail`` 个点的值），
        用最大似然估计 α，再算拟合分布和数据之间的 KS 距离（两条累积分布曲线
        的最大差距）。取 KS 距离最小的 ``xmin``。最后在同一段尾部上拟合一个
        离散指数分布（几何分布），算两个模型的对数似然比和它的显著性。

    实验做法
        实验 2b 把几千次雪崩的大小（以及持续时间）交给它，报告 α、``xmin``、
        尾部点数，以及"幂律 vs 指数"的结论；三种网格大小分别拟合，
        看 α 是否稳定、尾部是否随网格变长。

    目的和意义
        "双对数图上像一条直线"是判断幂律最常见、也最不可靠的方法：
        用最小二乘拟合直线会系统性地估错斜率，而且很多非幂律分布在一段范围内
        也像直线。最大似然 + KS 选下界 + 与替代分布的似然比检验，是 Clauset、
        Shalizi 和 Newman（2009）给出的标准做法。

    易错点
        - α 的估计只对尾部（x ≥ ``xmin``）有效；``xmin`` 选得太小，会被不服从
          幂律的小值拖偏；选得太大，尾部点太少、误差变大。
        - 似然比 > 0 只说明幂律比指数"更像"，还要看 ``p_value``：
          p 较大（例如 > 0.1）时，两者其实分不出来。
        - 有限尺寸截断会让最右端掉下去；这时幂律和指数都不完美，
          需要结合不同网格大小一起判断，而不是只看一个数。

    Reference
        Clauset, A., Shalizi, C. R., & Newman, M. E. J. (2009). Power-law
        distributions in empirical data. *SIAM Review*, 51(4), 661–703.
    """
    x = np.asarray(data, dtype=float)
    x = x[x >= 1]
    candidates = [v for v in np.unique(x) if np.sum(x >= v) >= min_tail]
    if not candidates:
        raise ValueError(f"need at least {min_tail} positive values")

    best = None
    for xmin in candidates:
        tail = x[x >= xmin]
        alpha = _alpha_mle(tail, int(xmin))
        ks = _ks_distance(tail, alpha, int(xmin))
        if best is None or ks < best[2]:
            best = (int(xmin), alpha, ks)
    xmin, alpha, ks = best
    tail = x[x >= xmin]
    n = len(tail)

    loglik_pl = -alpha * np.log(tail) - np.log(special.zeta(alpha, xmin))
    mean_excess = np.mean(tail - xmin)
    q = mean_excess / (1.0 + mean_excess)  # geometric MLE on x - xmin
    loglik_exp = np.log(1.0 - q) + (tail - xmin) * np.log(q) if q > 0 else np.zeros(n)
    diff = loglik_pl - loglik_exp
    ratio = float(diff.sum())
    sigma = float(diff.std())
    p_value = float(special.erfc(abs(ratio) / (sigma * np.sqrt(2 * n)))) if sigma > 0 else 0.0

    return PowerLawFit(
        alpha=float(alpha),
        alpha_err=float((alpha - 1) / np.sqrt(n)),
        xmin=xmin,
        n_tail=n,
        ks=float(ks),
        loglik_ratio=ratio,
        p_value=p_value,
    )
