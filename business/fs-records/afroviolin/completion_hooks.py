# completion_hooks.py
HOOKS = {
    'feature_complete': [
        'run_tests',
        'create_pull_request',
        'notify_slack'
    ],
    'tests_passing': [
        'update_documentation',
        'tag_release_candidate'
    ]
}
