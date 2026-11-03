struct Node
{
    int value;
    Node* next;
};

int sum_tail(Node* node)
{
    int sum = 0;
    while ((node = node->next) != nullptr) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-3]
    {
        sum += node->value;
    }
    return sum;
}

int main()
{
    Node third{3, nullptr};
    Node second{2, &third};
    Node first{1, &second};
    return sum_tail(&first);
}
