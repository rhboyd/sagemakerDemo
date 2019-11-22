from aws_cdk import (
    aws_apigateway as apigw,
    aws_iam as iam,
    core
)

from .hello_construct import HelloConstruct


class MyStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        my_api = apigw.RestApi(self, "SageMakerAPI", default_cors_preflight_options=apigw.CorsOptions(allow_origins=["*"], allow_headers=["*"], allow_methods=["*"]))
        endpoint_name = self.node.try_get_context("endpoint_name")

        options = apigw.IntegrationOptions(
            credentials_role=iam.Role(self, "SMInvoke",
                                      assumed_by=iam.ServicePrincipal("apigateway"),
                                      inline_policies={"FullSageMaker": iam.PolicyDocument(statements=[iam.PolicyStatement(actions=["*"], resources=["*"])])}
                                      ),
            integration_responses=[
                apigw.IntegrationResponse(
                    status_code="200",
                    response_templates={"application/json": ""},
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Headers": "'*'",
                        "method.response.header.Access-Control-Allow-Methods": "'*'",
                        "method.response.header.Access-Control-Allow-Origin": "'*'"

                    }
                )
            ]
        )

        integration = apigw.Integration(
            type=apigw.IntegrationType.AWS,
            uri="arn:aws:apigateway:us-east-1:runtime.sagemaker:path/endpoints/{}/invocations".format(self.node.try_get_context("endpoint_name")),
            integration_http_method="POST",
            options=options
        )

        apigw.Method(self, "PostRoot",
                     http_method="POST",
                     resource=my_api.root,
                     integration=integration,
                     options=apigw.MethodOptions(
                         method_responses=[
                             apigw.MethodResponse(
                                 status_code="200",
                                 response_parameters= {
                                     "method.response.header.Access-Control-Allow-Methods": True,
                                     "method.response.header.Access-Control-Allow-Headers": True,
                                     "method.response.header.Access-Control-Allow-Origin": True
                                 }
                             )
                         ]
                     )
        )

