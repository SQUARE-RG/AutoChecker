// positive_04.cpp

int main()
{
    auto classify = [](int value) {
        switch (value)
        {
            case 1:
                return 10;
            case 2:
                return 20;
        }
        return 0;
    };
    return classify(1);
}
