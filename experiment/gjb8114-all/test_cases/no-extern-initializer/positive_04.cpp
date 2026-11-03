struct Pair
{
    int first;
    int second;
};

extern Pair g_pair;
Pair g_pair = {1, 2};

int main()
{
    return g_pair.first + g_pair.second;
}
