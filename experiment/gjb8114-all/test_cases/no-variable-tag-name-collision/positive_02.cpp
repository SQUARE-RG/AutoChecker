struct Node
{
    int value;
    Node *next;
};

int sum(const Node &node_obj)
{
    return node_obj.value;
}

int main()
{
    Node node{7, nullptr};
    Node *node_ptr = &node;
    return sum(*node_ptr);
}
