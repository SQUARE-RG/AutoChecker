enum Singleton
{
    Only = 7
};

int main()
{
    Singleton s = Only;
    return static_cast<int>(s);
}
