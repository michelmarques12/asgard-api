import json
from unittest import TestCase, skip
from unittest.mock import patch, Mock
import responses
from copy import deepcopy

from marathon import NotFoundError, MarathonApp
from responses import RequestsMock

from hollowman import conf
from hollowman.app import application
from hollowman.hollowman_flask import HollowmanRequest
from hollowman.http_wrappers.request import Request
from hollowman.models import User, Account
from hollowman.marathon.group import SieveAppGroup
from hollowman.marathonapp import SieveMarathonApp

from tests.utils import with_json_fixture, get_fixture


class SplitTests(TestCase):

    def setUp(self):
        self.user = User(tx_name="User One", tx_email="user@host.com")
        self.user.current_account = Account(name="Dev", namespace="dev", owner="company")
        responses.start()

    def tearDown(self):
        responses.stop()

    # todo: debater nome request_app e app <- app fica ambíguo
    @with_json_fixture('single_full_app.json')
    def test_a_read_single_app_request_returns_a_single_marathonapp_if_app_exists(self, fixture):
        with application.test_request_context('/v2/apps//foo',
                                              method='GET', data=b'') as ctx:
            ctx.request.user = None
            request_parser = Request(ctx.request)

            with patch.object(request_parser, 'marathon_client') as client:
                client.get_app.return_value = MarathonApp.from_json(fixture)
                apps = list(request_parser.split())

            self.assertEqual(
                apps,
                [
                    (MarathonApp(), client.get_app.return_value)
                ])

    @with_json_fixture('requests/get-v2apps-all-apps.json')
    def test_a_request_with_n_apps_returns_n_marathonapps(self, fixture):
        with application.test_request_context('/v2/apps/', method='GET') as ctx:
            ctx.request.user = None
            request_parser = Request(ctx.request)
            with RequestsMock() as rsps:
                rsps.add(method='GET',
                         url=conf.MARATHON_ENDPOINT + '/v2/apps',
                         body=json.dumps(fixture),
                         status=200)
                apps = list(request_parser.split())

                request_apps = [request_app for request_app, _ in apps]
                self.assertEqual(request_apps, [MarathonApp()] * 4)

                self.assertEqual([app.id for _, app in apps],
                                 [app['id'] for app in fixture['apps']])

    @with_json_fixture('single_full_app.json')
    def test_a_request_for_a_new_app_will_return_a_tuple_with_an_empty_marathonapp(self, fixture):
        with application.test_request_context('/v2/apps//foo',
                                              method='PUT',
                                              data=json.dumps(fixture)) as ctx:
            ctx.request.user = None
            request_parser = Request(ctx.request)
            with patch.object(request_parser, 'marathon_client') as client:
                response_mock = Mock()
                response_mock.headers.get.return_value = 'application/json'
                client.get_app.side_effect = NotFoundError(response=response_mock)
                apps = list(request_parser.split())

            self.assertEqual(
                apps,
                [
                    (MarathonApp.from_json(fixture), MarathonApp())
                ]
            )

    @with_json_fixture('single_full_app.json')
    def test_a_request_for_write_operation_with_appid_in_url_path_returns_a_tuple_of_marathonapp(self, fixture):
        scale_up = {'instances': 10}
        with application.test_request_context('/v2/apps/foo',
                                              method='PUT',
                                              data=json.dumps(scale_up)) as ctx:
            ctx.request.user = None
            request_parser = Request(ctx.request)
            with RequestsMock() as rsps:
                rsps.add(method='GET',
                         url=conf.MARATHON_ENDPOINT + '/v2/apps//foo',
                         body=json.dumps({'app': fixture}),
                         status=200)
                apps = list(request_parser.split())
                expected_app = (MarathonApp(**scale_up), MarathonApp.from_json(fixture))
                self.assertEqual(apps, [expected_app])

    @with_json_fixture('single_full_app.json')
    def test_a_request_for_restart_operation_with_appid_in_url_path_returns_a_tuple_of_marathonapp(self, fixture):
        with application.test_request_context('/v2/apps/xablau/restart',
                                              method='PUT',
                                              data=b'{"force": true}') as ctx:
            ctx.request.user = None
            request_parser = Request(ctx.request)
            with RequestsMock() as rsps:
                rsps.add(method='GET',
                         url=conf.MARATHON_ENDPOINT + '/v2/apps//xablau',
                         body=json.dumps({'app': fixture}),
                         status=200)
                apps = list(request_parser.split())

                expected_app = (MarathonApp(), MarathonApp.from_json(fixture))
                self.assertEqual(apps, [expected_app])

    @with_json_fixture('single_full_app.json')
    def test_split_does_not_break_when_removing_force_parameter_if_request_is_a_list(self, fixture):
        request_data = {"id": "/foo", "instances": 2}
        with application.test_request_context('/v2/apps/',
                                              method='PUT',
                                              data=json.dumps(request_data)) as ctx:
            ctx.request.user = None
            request_parser = Request(ctx.request)
            with RequestsMock() as rsps:
                rsps.add(method='GET',
                         url=conf.MARATHON_ENDPOINT + '/v2/apps//foo',
                         body=json.dumps({'app': fixture}),
                         status=200)
                apps = list(request_parser.split())

                expected_app = (MarathonApp.from_json(request_data), MarathonApp.from_json(fixture))
                self.assertEqual(apps, [expected_app])

    @with_json_fixture("single_full_app.json")
    def test_can_read_app_if_already_migrated(self, single_full_app_fixture):
        """
        Conferimos que é possível fazer um GET em
        /v2/apps/<app-id> para uma app que já está migrada.
        O <app-id> usado é sempre *sem* namespace
        """
        request_data = deepcopy(single_full_app_fixture)
        single_full_app_fixture['id'] = '/dev/foo'
        with application.test_request_context('/v2/apps/foo', method='GET') as ctx:
            ctx.request.user = self.user
            request_parser = Request(ctx.request)
            with RequestsMock() as rsps:
                #rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/apps//foo',
                #         body=json.dumps({'message': "App /foo not found"}), status=404)
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/apps//dev/foo',
                         body=json.dumps({'app': single_full_app_fixture}), status=200)

                apps = list(request_parser.split())

                expected_app = (MarathonApp(), MarathonApp.from_json(single_full_app_fixture))
                self.assertEqual(apps, [expected_app])

    @with_json_fixture("single_full_app.json")
    def test_can_read_app_still_not_migradted(self, single_full_app_fixture):
        """
        Conferimos que é possível fazer um GET em
        /v2/apps/<app-id> para uma app que já *não* está migrada.
        O <app-id> usado é sempre *sem* namespace
        """
        request_data = deepcopy(single_full_app_fixture)
        with application.test_request_context('/v2/apps/foo', method='GET') as ctx:
            ctx.request.user = self.user
            request_parser = Request(ctx.request)
            with RequestsMock() as rsps:
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/apps//dev/foo',
                         body=json.dumps({'message': "App /foo not found"}), status=404)
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/apps//foo',
                         body=json.dumps({'app': single_full_app_fixture}), status=200)

                apps = list(request_parser.split())

                expected_app = (MarathonApp(), MarathonApp.from_json(single_full_app_fixture))
                self.assertEqual(apps, [expected_app])

    @with_json_fixture("../fixtures/group_dev_namespace_with_apps.json")
    def test_split_groups_read_on_root_group(self, group_dev_namespace_fixture):

        with application.test_request_context('/v2/groups', method='GET') as ctx:
            ctx.request.user = self.user
            request_parser = Request(ctx.request)
            with RequestsMock() as rsps:
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/groups//dev/',
                         body=json.dumps(group_dev_namespace_fixture), status=200)

                apps = list(request_parser.split())
                self.assertEqual(3, len(apps))

                expected_apps = [
                    (MarathonApp(), MarathonApp.from_json({"id": "/dev/a/app0"})),
                    (MarathonApp(), MarathonApp.from_json({"id": "/dev/group-b/appb0"})),
                    (MarathonApp(), MarathonApp.from_json({"id": "/dev/group-b/group-b0/app0"})),
                ]
                self.assertEqual(apps, expected_apps)

    @with_json_fixture("../fixtures/group-b_dev_namespace_with_apps.json")
    def test_split_groups_read_on_specific_group(self, group_b_fixture):

        with application.test_request_context('/v2/groups/group-b', method='GET') as ctx:
            ctx.request.user = self.user
            request_parser = Request(ctx.request)
            with RequestsMock() as rsps:
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/groups//dev/group-b',
                         body=json.dumps(group_b_fixture), status=200)

                apps = list(request_parser.split())
                self.assertEqual(2, len(apps))

                expected_apps = [
                    (MarathonApp(), MarathonApp.from_json({"id": "/dev/group-b/appb0"})),
                    (MarathonApp(), MarathonApp.from_json({"id": "/dev/group-b/group-b0/app0"})),
                ]
                self.assertEqual(expected_apps, apps)

    @skip("Temos que pensar sobre esse method no grupo")
    def test_split_groups_write_PUT_on_group(self):
        """
        Atualmente, o único body que chega em um PUT em /v2/groups é:
            {"scaleBy": <N>}
        onde `<N>` é o fator que será multiplicado pelo atual número de TASK_RUNNING de cada app.

        O problema é que o Request.split() retorna uma lista de apps, e o Request.join() potencialmente
        vai reconstruir um body com essa lista de apps. O problema é que isso gera um request body *diferente* do orignal,
        já que agora temos um body contendo um APP_GROUP com todas suas apps (e sub apps).

        E se fazemos apenas isso, a informação do "scaleBy" se perdeu, pois se mandamos um request com o TASK_GROUP inteiro para o
        upstream, nada vai mudar já que as apps não foram modificadas.

        Uma ideia é o Core do hollowman decobrir essa ação de scaleBy e chamar o métoro "scale_by" dos filtros, já com a request_app tendo seu
        atributo "instances" multiplicado pelo fator. Opcionalmente o fator poderia ser passado como parametro para o filtro.

        Isso nos daria a possibilidade de "corrigir" um problema atual do scaleby que é:
            Quando damos scale_by = 2 em um app que está suspended, ela continua suspended já que 2 * 0 = 0. A ideia é que suspended apps também sejam
            ligadas considerando esse fator. O que faríamos no filtro seria, para toda app que instances = 0, consideramos instances = 1 e multiplicamos pelo fator.

        Enfim, apenas uma ideia. Temos que ver o que fazemos com esse teste aqui.
        """

        with application.test_request_context('/v2/groups/group-b', method='PUT') as ctx:
            ctx.request.user = self.user
            request_parser = Request(ctx.request)
            with RequestsMock() as rsps:
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/groups//dev/group-b',
                         body=json.dumps(group_b_fixture), status=200)

                apps = list(request_parser.split())
                self.assertEqual(2, len(apps))

                expected_apps = [
                    (MarathonApp(), MarathonApp.from_json({"id": "/dev/group-b/appb0"})),
                    (MarathonApp(), MarathonApp.from_json({"id": "/dev/group-b/group-b0/app0"})),
                ]
                self.assertEqual(expected_apps, apps)

    @with_json_fixture("non_root_group_empty.json")
    def test_split_group_nonroot_empty_group(self, non_root_group_empty_fixture):
        with application.test_request_context('/v2/groups/group-c', method='GET') as ctx:
            ctx.request.user = self.user
            request_parser = Request(ctx.request)
            with RequestsMock() as rsps:
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/groups//dev/group-c',
                         body=json.dumps(non_root_group_empty_fixture), status=200)

                apps = list(request_parser.split())
                self.assertEqual(0, len(apps))

                self.assertEqual([], apps)


class JoinTests(TestCase):

    def setUp(self):
        self.user = User(tx_name="User One", tx_email="user@host.com")
        self.user.current_account = Account(name="Dev", namespace="dev", owner="company")

    @with_json_fixture('single_full_app.json')
    def test_it_recreates_a_get_request_for_a_single_app(self, fixture):
        with application.test_request_context('/v2/apps//foo',
                                              method='GET', data=b'') as ctx:
            ctx.request.user = None
            request_parser = Request(ctx.request)
            with patch.object(request_parser, 'marathon_client') as client:
                client.get_app.return_value = MarathonApp.from_json(fixture)
                apps = list(request_parser.split())

                request = request_parser.join(apps)
                self.assertIsInstance(request, HollowmanRequest)
                self.assertEqual(request, ctx.request)
                self.assertEqual(request.data, b'')

    @with_json_fixture('single_full_app.json')
    def test_it_recreates_a_put_request_for_a_single_app(self, fixture):
        with application.test_request_context('/v2/apps//foo',
                                              method='PUT',
                                              data=json.dumps(fixture)) as ctx:
            ctx.request.user = None
            request_parser = Request(ctx.request)
            with patch.object(request_parser, 'marathon_client') as client:
                client.get_app.return_value = MarathonApp.from_json(fixture)
                apps = list(request_parser.split())

                request = request_parser.join(apps)
                self.assertIsInstance(request, HollowmanRequest)
                self.assertEqual(request.get_json()['id'], '/foo')

    @with_json_fixture('single_full_app.json')
    def test_it_recreates_a_post_request_for_a_single_app(self, fixture):
        with application.test_request_context('/v2/apps//foo',
                                              method='POST',
                                              data=json.dumps(fixture)) as ctx:
            ctx.request.user = None
            request_parser = Request(ctx.request)
            with patch.object(request_parser, 'marathon_client') as client:
                client.get_app.return_value = MarathonApp.from_json(fixture)
                apps = list(request_parser.split())

                request = request_parser.join(apps)
                self.assertIsInstance(request, HollowmanRequest)
                self.assertEqual(request.get_json()['id'], '/foo')

    @with_json_fixture('requests/put-multi-app.json')
    def test_it_recreates_a_put_request_for_multiple_apps(self, fixture):
        with application.test_request_context('/v2/apps/',
                                              method='PUT',
                                              data=json.dumps(fixture)) as ctx:
            ctx.request.user = None
            request_parser = Request(ctx.request)
            mock_app = get_fixture('single_full_app.json')
            mock_apps = [(MarathonApp.from_json(mock_app), Mock()) for _ in range(2)]

            request = request_parser.join(mock_apps)
            self.assertIsInstance(request, HollowmanRequest)
            self.assertCountEqual(
                [app['id'] for app in json.loads(request.data)],
                [app.id for app, _ in mock_apps]
            )

    @with_json_fixture("single_full_app.json")
    def test_change_request_path_if_is_read_single_app(self, single_full_app_fixture):
        with application.test_request_context('/v2/apps/foo',
                                              method='GET') as ctx:
            ctx.request.user = self.user
            request_parser = Request(ctx.request)
            single_full_app_fixture['id'] = "/dev/foo"
            apps = [(MarathonApp.from_json(single_full_app_fixture), MarathonApp.from_json(single_full_app_fixture))]

            request = request_parser.join(apps)
            self.assertIsInstance(request, HollowmanRequest)
            self.assertEqual("/v2/apps/dev/foo", request.path)

    @with_json_fixture("single_full_app.json")
    def test_change_request_path_if_is_write_on_one_app(self, fixture):
        """
        Quando fazemos WRITE em cima de uma app específica, devemos
        ajustar o request.path para que o `upstream_request` seja feito
        no endpoint correto.
        """
        user = User(tx_name="User One", tx_email="user@host.com")
        user.current_account = Account(name="Dev", namespace="dev", owner="company")

        full_app_with_name_space = deepcopy(fixture)
        full_app_with_name_space['id'] = "/dev/foo"
        with application.test_request_context('/v2/apps//foo', method='PUT',
                                              data=json.dumps(fixture)) as ctx:
            with RequestsMock() as rsps:
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/apps//dev/foo',
                              body=json.dumps({'app': full_app_with_name_space}), status=200)
                ctx.request.user = user
                request_parser = Request(ctx.request)

                apps = list(request_parser.split())

                request = request_parser.join(apps)
                self.assertIsInstance(request, HollowmanRequest)
                self.assertEqual("/v2/apps/dev/foo", request.path)

    @with_json_fixture("../fixtures/group_dev_namespace_with_apps.json")
    def test_join_group_read_root_group(self, group_dev_namespace_fixture):
        with application.test_request_context('/v2/groups', method='GET') as ctx:
            ctx.request.user = self.user
            request = Request(ctx.request)
            with RequestsMock() as rsps:
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/groups//dev/',
                         body=json.dumps(group_dev_namespace_fixture), status=200)

                apps = list(request.split())
                joined_request = request.join(apps)
                self.assertEqual("/v2/groups/dev", joined_request.path)
                self.assertEqual(b"", joined_request.data)

    @with_json_fixture("../fixtures/group-b_dev_namespace_with_apps.json")
    def test_join_group_read_non_root_group(self, group_b_fixture):
        with application.test_request_context('/v2/groups/group-b', method='GET') as ctx:
            ctx.request.user = self.user
            request = Request(ctx.request)
            with RequestsMock() as rsps:
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/groups//dev/group-b',
                         body=json.dumps(group_b_fixture), status=200)

                apps = list(request.split())
                joined_request = request.join(apps)
                self.assertEqual("/v2/groups/dev/group-b", joined_request.path)
                self.assertEqual(b"", joined_request.data)

    @with_json_fixture("../fixtures/non_root_group_empty.json")
    def test_join_group_read_non_root_empty_group(self, non_root_group_empty_fixture):
        with application.test_request_context('/v2/groups/group-c', method='GET') as ctx:
            ctx.request.user = self.user
            request = Request(ctx.request)
            with RequestsMock() as rsps:
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/groups//dev/group-c',
                         body=json.dumps(non_root_group_empty_fixture), status=200)

                apps = list(request.split())
                joined_request = request.join(apps)
                self.assertEqual("/v2/groups/dev/group-c", joined_request.path)
                self.assertEqual(b"", joined_request.data)

    @skip("Decidir como implementar PUT em /v2/groups")
    def test_join_group_write_PUT_request(self):
        """
        O resultado o body do request deve ser a represebtação de todo o grupo,
        com seus subgrupos e apps.
        """
        self.fail()


class GetOriginalGroupTest(TestCase):

    def setUp(self):
        self.user = User(tx_name="User One", tx_email="user@host.com")
        self.user.current_account = Account(name="Dev", namespace="dev", owner="company")

    def test_get_original_group_not_yet_migrated(self):
        found_group = {
            "id": "/not-migrated",
            "apps": [],
            "groups": [],
        }
        with application.test_request_context('/v2/groups//not-migrated',
                                              method='GET') as ctx:
            with RequestsMock() as rsps:
                rsps.add(method='GET',
                         url=conf.MARATHON_ENDPOINT + '/v2/groups//dev/not-migrated',
                         status=404)
                rsps.add(method='GET',
                         url=conf.MARATHON_ENDPOINT + '/v2/groups//not-migrated',
                         body=json.dumps(found_group),
                         status=200)
                ctx.request.user = self.user
                request = Request(ctx.request)

                group = request._get_original_group(self.user, "/not-migrated")
                self.assertEqual(SieveAppGroup().from_json(found_group), group)

    def test_get_original_group_migrated(self):
        found_group = {
            "id": "/dev/foo",
            "apps": [],
            "groups": [],
        }
        with application.test_request_context('/v2/groups//foo',
                                              method='GET') as ctx:
            with RequestsMock() as rsps:
                rsps.add(method='GET',
                         url=conf.MARATHON_ENDPOINT + '/v2/groups//dev/foo',
                         body=json.dumps(found_group),
                         status=200)
                ctx.request.user = self.user
                request = Request(ctx.request)

                group = request._get_original_group(self.user, "/foo")
                self.assertTrue(isinstance(group, SieveAppGroup))
                self.assertEqual(SieveAppGroup().from_json(found_group), group)

    def test_get_original_group_not_found(self):
        """
        Tenta buscar um grupo que não existe.
        """
        with application.test_request_context('/v2/groups//not-found',
                                              method='GET') as ctx:
            with RequestsMock() as rsps:
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/groups//dev/not-found', status=404)
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/groups//not-found', status=404)
                ctx.request.user = self.user
                request = Request(ctx.request)

                group = request._get_original_group(self.user, "/not-found")
                self.assertEqual(SieveAppGroup(), group)
