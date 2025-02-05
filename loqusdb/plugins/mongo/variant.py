import logging

from loqusdb.plugins import BaseVariantMixin

logger = logging.getLogger(__name__)

class VariantMixin(BaseVariantMixin):
    
    def add_variant(self, variant):
        """Add a variant to the variant collection
        
            If the variant exists we update the count else we insert a new variant
            object.
        
            Args:
                variant (dict): A variant dictionary
        
        """
        logger.debug("Upserting variant: {0}".format(variant.get('_id')))
        
        if variant.get('family_id'):
            message = self.db.variant.update(
                {'_id': variant['_id']},
                {
                    '$inc': {
                        'homozygote': variant.get('homozygote', 0),
                        'hemizygote': variant.get('hemizygote', 0),
                        'observations': 1
                    },
                    '$push': {
                        'families': {
                            '$each': [variant.get('family_id')],
                            '$slice': -50
                            }
                        }
                 }, 
                 upsert=True
            )
        else:
            message = self.db.variant.update(
                {'_id': variant['_id']},
                {
                    '$inc': {
                        'homozygote': variant.get('homozygote', 0),
                        'hemizygote': variant.get('hemizygote', 0),
                        'observations': 1,
                    }
                 }, 
                 upsert=True
            )
            
    
        if message.get('updatedExisting'):
            logger.debug("Variant {0} was updated".format(message.get("upserted")))
        else:
            logger.debug("Variant was added to database for first time")
        return
    
    def get_variant(self, variant):
        """Check if a variant exists in the database and return it
    
            Search the variants with the variant id
        
            Args:
                variant (dict): A variant dictionary
        
            Returns:
                variant (dict): A variant dictionary
        """
        return self.db.variant.find_one({'_id': variant.get('_id')})

    def get_variants(self):
        """Return all variants in the database
    
            Returns:
                variants (Iterable(Variant))
        """
        return self.db.variant.find()

    def delete_variant(self, variant):
        """Remove variant from database
            
            This means that we take down the observations variable with one.
            If 'observations' == 1 we remove the variant. If variant was homozygote
            we decrease 'homozygote' with one.
            
            Args:
                variant (dict): A variant dictionary            
        """
        mongo_variant = self.get_variant(variant)
        
        if mongo_variant:
            
            if mongo_variant['observations'] == 1:
                logger.debug("Removing variant {0}".format(
                    mongo_variant.get('_id')
                ))
                message = self.db.variant.remove({'_id': variant['_id']})
            else:
                logger.debug("Decreasing observations for {0}".format(
                    mongo_variant.get('_id')
                ))
                message = self.db.variant.update({
                    '_id': mongo_variant['_id']
                    },{
                        '$inc': {
                            'observations': -1,
                            'homozygote': - (variant.get('homozygote', 0)),
                            'hemizygote': - (variant.get('hemizygote', 0)),
                        },
                        '$pull': {
                            'families': variant.get('family_id')
                        }
                    }, upsert=False)
        return
