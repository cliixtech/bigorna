import click

from bigorna import __VERSION__
from bigorna.commons import Config


pass_config = click.make_pass_decorator(Config)


@click.group()
@click.version_option(version=__VERSION__)
@click.option('--config', default='config.yml', type=click.Path(),
              help="Configuration file path")
@click.pass_context
def main(ctx, config):
    cfg = Config(config)
    click.secho("Loading configuration from file %s" % config, fg='green')
    ctx.obj = cfg


@main.command(help="Run http server")
@pass_config
def runserver(cfg):
    import logging
    from bigorna.core import Bigorna
    from bigorna.http import app

    app.bigorna = Bigorna.new(cfg)
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s:%(levelname)s:%(name)s:%(message)s",
                        datefmt='%Y-%m-%dT%H:%M:%S')
    app.run(host="0.0.0.0", port=5555, debug=True)


@main.command(help="Run http server")
@pass_config
def create_db(cfg):
    click.secho("Creating db on file %s" % cfg.db_file, fg='green')
    from bigorna.tracker.persistence import Base, create_engine
    Base.metadata.create_all(create_engine(cfg))
