enum Color { Red, Green, Blue };

int classify(Color c)
{
    switch (c) {
        case Red:
            return 1;
        case Green:
            return 2;
        case Blue:
            return 3;
    }
    return 0;
}

int main()
{
    return classify(Green);
}
