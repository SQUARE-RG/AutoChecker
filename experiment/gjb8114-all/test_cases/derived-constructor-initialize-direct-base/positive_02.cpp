#include <iostream>

class Document {
public:
    Document() : docid(0) {}
    explicit Document(int value) : docid(value) {}
    int docid;
};

class Archive {
public:
    Archive() : slot(0) {}
    explicit Archive(int value) : slot(value) {}
    int slot;
};

class Book : public Document, public Archive {
public:
    Book(int value);
    int bookid;
};

Book::Book(int value) : Document(value), Archive(value), bookid(value)
{
}

int main() {
    Book mybook(2);
    std::cout << mybook.bookid << mybook.docid << mybook.slot << '\n';
    return 0;
}
