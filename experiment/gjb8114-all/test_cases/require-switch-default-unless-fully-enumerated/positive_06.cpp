int classify(char c)
{
    int result = 0;
    switch (c) {
        case 'a':
            result = 1;
            break;
        case 'b':
            result = 2;
            break;
        default:
            result = -1;
            break;
    }
    return result;
}

int main()
{
    return classify('a');
}
