#include <iostream>

struct Renderer {
    virtual void render();
    virtual ~Renderer();
};

Renderer::~Renderer() {}

void Renderer::render() {}

int main() {
    return 0;
}
