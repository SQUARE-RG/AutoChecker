#include <iostream>

struct Node
{
    int value;
};

int main()
{
    Node node{7};
    const void* generic = static_cast<const void*>(&node);
    return generic != nullptr ? 0 : 1;
}
