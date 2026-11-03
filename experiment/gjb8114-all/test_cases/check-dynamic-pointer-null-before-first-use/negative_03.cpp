#include <cstdlib>

struct Node {
    int value;
};

int main() {
    Node* node = static_cast<Node*>(std::malloc(sizeof(Node)));
    node->value = 42; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-8]
    std::free(node);
    return 0;
}
