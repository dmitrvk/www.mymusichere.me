# Licensed under the MIT License

import json
import logging
import operator
from typing import List

from django import http, views
from django.conf import settings
from django.utils.decorators import method_decorator
from scores import models


class PublishView(views.View):
    """Publish scores on the website."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @method_decorator(views.decorators.csrf.csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(PublishView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        if 'Authorization' not in request.headers:
            return http.HttpResponseBadRequest()

        auth_header = request.headers.get('Authorization', 'None')

        if auth_header != f'Token {settings.PUBLISH_TOKEN}':
            return http.HttpResponseBadRequest()

        scores_headers = json.loads(request.body.decode())
        slugs = list(map(
            operator.itemgetter('slug'), scores_headers))

        # Delete scores which were removed from repository
        models.Score.objects.exclude(slug__in=slugs).delete()
        self.logger.info('Redundant scores deleted.')

        # Update scores or create new ones
        for score_header in scores_headers:
            self.logger.info("Processing score '%s'", score_header['slug'])
            self._create_or_update_score(score_header)

        self.logger.info("Published successfully.")
        return http.HttpResponse('Scores published.')

    def _create_or_update_score(self, score_header: List[dict]) -> None:
        score_properties = score_header.copy()

        # Default assignment in many-to-many is restricted,
        # so handle instruments later, when score already exists
        del score_properties['instruments']

        if 'composer' in score_header:
            composer = self._get_or_create_composer(score_header['composer'])
            score_properties['composer'] = composer

        if 'arranger' in score_header:
            arranger = self._get_or_create_arranger(score_header['arranger'])
            score_properties['arranger'] = arranger

        score, created = models.Score.objects.get_or_create(
            slug=score_header['slug'], defaults=score_properties,
        )

        if created:
            print('Score', score.slug, 'created')
            self.logger.info("Score '%s' created", score.slug)
        else:
            score.title = score_properties['title']

            if 'composer' in score_properties:
                score.composer = score_properties['composer']

            if 'arranger' in score_properties:
                score.arranger = score_properties['arranger']

            self.logger.info("Score '%s' updated", score.slug)

        if 'instruments' in score_header:
            instruments = self._get_or_create_instruments(
                score_header['instruments'])
            score.instruments.set(instruments)

        self.logger.info("Instruments for score '%s' updated", score.slug)

        score.save()

    def _get_or_create_composer(
            self, score_header_composer: dict) -> models.Composer:
        composer_name = score_header_composer

        composer, created = models.Composer.objects.get_or_create(
            name=composer_name
        )

        if created:
            self.logger.info("Composer '%s' created", composer.name)
        else:
            self.logger.info("Composer '%s' already exists", composer.name)

        return composer

    def _get_or_create_arranger(
            self, score_header_arranger: dict) -> models.Arranger:
        arranger_name = score_header_arranger

        arranger, created = models.Arranger.objects.get_or_create(
            name=arranger_name
        )

        if created:
            self.logger.info("Arranger '%s' created", arranger.name)
        else:
            self.logger.info("Arranger '%s' already exists", arranger.name)

        return arranger

    def _get_or_create_instruments(
            self, score_header_instruments: str) -> list:
        instruments_names = score_header_instruments

        instruments = []

        for instrument_name in instruments_names.split():
            instrument, created = models.Instrument.objects.get_or_create(
                name=instrument_name
            )

            if created:
                self.logger.info("Instrument '%s' created", instrument.name)
            else:
                message = "Instrument '%s' already exists"
                self.logger.info(message, instrument.name)

            instruments.append(instrument)

        return instruments
