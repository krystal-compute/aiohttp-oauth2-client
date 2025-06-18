@Library('lib')_

pythonPipeline {
  package_name            = 'aiohttp_oauth2_client'
  python_version          = ['3.10', '3.11', '3.12']
  create_tag_job          = true
  upload_pypi             = true
  run_tests               = true
  extras_require          = 'dev'
  enable_caching          = true
  enable_uv               = true
}