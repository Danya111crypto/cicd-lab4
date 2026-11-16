describe("Login Form E2E Test", () => {
  it("should log in user using fixture data and mocked API response", () => {
    cy.intercept("POST", "/api/login", {
      statusCode: 200,
      body: { token: "fake-jwt-token" }
    }).as("loginRequest");

    cy.fixture("user").then((user) => {
      cy.visit("/login");

      cy.get('input[name="email"]')
        .type(user.email)
        .should("have.value", user.email);

      cy.get('input[name="password"]')
        .type(user.password)
        .should("have.value", user.password);

      cy.get('button[type="submit"]').click();

      cy.wait("@loginRequest");
      cy.url().should("include", "/dashboard");
      cy.contains(`Welcome, ${user.email}`).should("be.visible");
    });
  });
});