from studies.tool_ecology.scripts.plot_reuse_graph import cross_request_pairs


def test_graph_counts_each_correct_request_once_per_actual_package_pair():
    details = [
        dict(
            correct=True,
            family="clean",
            executed_edges=[
                "published.a01_r02->published.a00_r01.clean",
                "published.a01_r02->published.a00_r01.Helper.fill",
                "published.a01_r02->published.a01_r01.clean",
            ],
        ),
        dict(
            correct=True,
            family="lookup",
            executed_edges=[
                "published.a01_r02.adapter->published.a00_r01.sub.lookup",
            ],
        ),
        dict(
            correct=False,
            family="group",
            executed_edges=[
                "published.a01_r02->published.a00_r01.group",
            ],
        ),
    ]
    assert cross_request_pairs(details) == {("a01_r02", "a00_r01"): {"clean": 1, "lookup": 1}}


def test_graph_does_not_invent_proxy_execution_for_transitive_reexport():
    details = [
        dict(
            correct=True,
            family="clean",
            executed_edges=[
                "published.a02_r03->published.a00_r01.clean",
            ],
        )
    ]
    assert cross_request_pairs(details) == {("a02_r03", "a00_r01"): {"clean": 1}}
