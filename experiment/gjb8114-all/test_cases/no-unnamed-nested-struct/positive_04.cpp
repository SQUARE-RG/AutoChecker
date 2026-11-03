struct TreeNode
{
    int id;
    struct Payload
    {
        int weight;
    } payload = { 0 };
};

int main()
{
    TreeNode node{};
    node.id = 1;
    node.payload.weight = 3;
    return 0;
}
