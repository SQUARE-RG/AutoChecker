#include <iostream>

struct Node
{
    int id;
};

bool comesBefore(const Node* lhs, const Node* rhs)
{
    return lhs->id < rhs->id;
}

int main()
{
    Node a{1};
    Node b{2};
    std::cout << (comesBefore(&a, &b) ? "yes" : "no") << '\n';
    return 0;
}
