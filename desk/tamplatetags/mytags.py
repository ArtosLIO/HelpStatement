from django import template


register = template.Library()

@register.filter(name='filter_first')
def filter_first(self, statement_id):
    comment = self.filter(statement=statement_id).last()
    if not comment:
        return 'None'
    else:
        return comment.text
