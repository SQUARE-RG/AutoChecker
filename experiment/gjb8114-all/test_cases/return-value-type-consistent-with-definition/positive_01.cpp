unsigned int fun(unsigned int par)
{
    return par + 1u;
}

int main()
{
    unsigned int result = fun(1u);
    return static_cast<int>(result);
}
