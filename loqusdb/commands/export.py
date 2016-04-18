import logging
import click
import tempfile

from vcftoolbox import HeaderParser, sort_variants

logger = logging.getLogger(__name__)

from . import base_command


@base_command.command()
@click.pass_context
def export(ctx):
    """Export the variants of a loqus db
        
        The variants are exported to a vcf file
    """
    adapter = ctx.obj['adapter']
    
    logger.info("Export the variants from {0}".format(adapter))
    nr_cases = 0
    
    for nr_cases, case in enumerate(adapter.cases()):
        nr_cases += 1
    logger.info("Found {0} cases in database".format(nr_cases))
    head = HeaderParser()
    head.add_fileformat("##fileformat=VCFv4.1")
    head.add_meta_line("NrCases", nr_cases)
    head.add_info("Obs", '1', 'Integer', "The number of observations for the variant")
    head.add_info("Hom", '1', 'Integer', "The number of observed homozygotes")
    
    variants = tempfile.TemporaryFile()
    
    for line in head.print_header():
        print(line)
    
    try:
        for variant in adapter.get_variants():
            variant_id = variant['_id'].split('_')
            chrom = variant_id[0]
            pos = variant_id[1]
            ref = variant_id[2]
            alt = variant_id[3]
            
            observations = variant['observations']
            homozygotes = variant['homozygote']
            
            info = "Obs={0};Hom={1}".format(observations, homozygotes)
            
            variant_line = "{0}\t{1}\t.\t{2}\t{3}\t.\t.\t{4}\n".format(
                chrom, pos, ref, alt, info)
            
            variants.write(variant_line)
        
        variants.seek(0)
        for line in sort_variants(variants):
            print(line)
    finally:
        variants.close()