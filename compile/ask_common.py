"""Small shared contract for the wiki and its private subscription service."""
import json

MAX_CONTEXT = 200_000
MAX_ARTICLES = 12
DEADLINE_SECONDS = 240
MAX_WIRE = 2_000_000


class AskError(Exception):
    def __init__(self, message, status=503):
        super().__init__(message)
        self.status = status


def resolve_effort(model, effort=None):
    if effort is None:
        effort = model['default_effort']
    if not isinstance(effort, str) or effort not in model['effort_levels']:
        raise AskError('This effort level is not supported for the selected model.', 400)
    return effort


SCHEMAS = {
    'select': {
        'type': 'object', 'additionalProperties': False,
        'properties': {'article_ids': {'type': 'array', 'maxItems': MAX_ARTICLES,
                                      'items': {'type': 'string'}}},
        'required': ['article_ids'],
    },
    'answer': {
        'type': 'object', 'additionalProperties': False,
        'properties': {
            'paragraphs': {'type': 'array', 'maxItems': 20, 'items': {
                'type': 'object', 'additionalProperties': False,
                'properties': {'text': {'type': 'string'},
                               'article_ids': {'type': 'array', 'items': {'type': 'string'}}},
                'required': ['text', 'article_ids']}},
            'insufficient_evidence': {'type': 'boolean'},
        },
        'required': ['paragraphs', 'insufficient_evidence'],
    },
}


from knowledge_review import SCHEMAS as WORKFLOW_SCHEMAS, validate as validate_workflow
SCHEMAS.update(WORKFLOW_SCHEMAS)


def read_json(handler, limit=MAX_WIRE):
    try:
        if handler.headers.get('Transfer-Encoding'):
            raise ValueError()
        if handler.headers.get_content_type() != 'application/json':
            raise ValueError()
        length = int(handler.headers.get('Content-Length', '0'))
        if not 0 < length <= limit:
            raise ValueError()
        return json.loads(handler.rfile.read(length))
    except (ValueError, UnicodeError):
        raise AskError('Invalid or oversized JSON request.', 400) from None


def validate_result(stage, result):
    if stage in WORKFLOW_SCHEMAS:
        try:
            return validate_workflow(WORKFLOW_SCHEMAS[stage], result)
        except ValueError:
            raise AskError('The model returned an invalid workflow response.', 502) from None
    if not isinstance(result, dict) or set(result) != set(SCHEMAS[stage]['required']):
        raise AskError('The model returned an invalid response. Please retry.', 502)
    def ids(value):
        return (isinstance(value, list) and len(value) <= MAX_ARTICLES
                and all(isinstance(v, str) and 0 < len(v) <= 200 for v in value)
                and len(set(value)) == len(value))
    if stage == 'select':
        valid = ids(result['article_ids'])
    else:
        paragraphs = result['paragraphs']
        valid = (type(result['insufficient_evidence']) is bool
                 and isinstance(paragraphs, list) and 0 < len(paragraphs) <= 20)
        if valid:
            valid = all(isinstance(p, dict) and set(p) == {'text', 'article_ids'}
                        and isinstance(p['text'], str) and 0 < len(p['text']) <= 12000
                        and ids(p['article_ids']) for p in paragraphs)
    if not valid:
        raise AskError('The model returned an invalid response. Please retry.', 502)
    return result
