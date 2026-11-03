#include <iostream>

class Node {
public:
    Node() : value(3) {}
    int value;
};

void *eraseType(Node *n) {
    return reinterpret_cast<void*>(n);
}

int main() {
    Node *node = new Node();
    void *opaque = eraseType(node);
    std::cout << opaque << std::endl;
    delete node;
    return 0;
}
