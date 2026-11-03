#include <cstdlib>

struct Node {
    int value;
};

int main() {
    Node* node = static_cast<Node*>(std::malloc(sizeof(Node)));
    if (node == nullptr) {
        return 1;
    }
    node->value = 42;
    std::free(node);
    return 0;
}
