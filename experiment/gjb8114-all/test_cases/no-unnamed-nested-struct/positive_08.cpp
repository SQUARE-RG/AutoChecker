struct Registry
{
    struct Key { static constexpr int bits = 8; int value; } key;
    int count;
};

int main()
{
    Registry registry;
    registry.count = 3;
    registry.key.value = Registry::Key::bits;
    return registry.key.value == registry.count + 5 ? 0 : 1;
}
