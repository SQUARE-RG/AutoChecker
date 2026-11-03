#include <iostream>

struct Renderer {
    virtual void render();
    ~Renderer(); // CHECK-MESSAGES: :[[@LINE]]:5: warning: {{.*}} [ucassaat-r-2-3-1]
};

Renderer::~Renderer() {}

void Renderer::render() {}

int main() {
    return 0;
}
