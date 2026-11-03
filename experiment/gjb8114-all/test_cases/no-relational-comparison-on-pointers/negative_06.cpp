#include <iostream>

struct Node
{
    int value;
};

bool comesBefore(const Node* lhs, const Node* rhs)
{
    return lhs < rhs; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-2]
}

int main()
{
    Node nodes[2] = {{1}, {2}};
    std::cout << (comesBefore(&nodes[0], &nodes[1]) ? "yes" : "no") << '\n';
    return 0;
}
