template <typename Predicate>
void spin_until(Predicate done)
{
    while (1)
    {
        if (done())
        {
            break;
        }
    }
}

int main()
{
    spin_until([] { return true; });
    return 0;
}
