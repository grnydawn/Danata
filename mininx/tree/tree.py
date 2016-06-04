from mininx.classes.ordered import OrderedDiGraph

class Tree(OrderedDiGraph):
    '''
NOTE:
 - create a root node when a tree is created
 - adding subnode is the same to adding an edge
'''

    def __init__(self, data=None, **attr):
        super(self, Tree).__init__(data, **attr)

        self.root = object()
        self.add_node(self.root)

    def append_subnode(self, subnode, parent, data=None, **attr):
        pass

    def insert_subnode(self, index, subnode, parent, data=None, **attr):
        pass

    def remove_subnode(self, subnode, parent):
        pass

    def update_subnode(self, subnode, parent, data=None, **attr):
        pass

    def index_subnode(self, subnode, parent):
        pass
'''
tree functions



node functions



edge functions



get_name
is_empty
get_root
get_size
get_height
set_name
insert
remove
delete
search
dump
Count returns the number of nodes below the current node + 1 for the current node. The root node is not counted. 
DirectChildCount returns just the number of direct children of the current node. 
The Depth of a node is the number of parents it has, not including the root node. Thus, the depth of a top node is 0 and the depth of a top nodes child is 1, etc. 
A branch is a collection of sibling nodes. 
BranchCount is the number of sibling nodes and 
BranchIndex is the zero-based index of the current node in its branch.
    INode<T> Parent { get; }
    INode<T> Previous { get; }
    INode<T> Next { get; }
    INode<T> Child { get; }

    INode<T> Root { get; }
    INode<T> Top { get; }
    INode<T> First { get; }
    INode<T> Last { get; }

    INode<T> LastChild { get; }

    bool IsTree { get; }
    bool IsRoot { get; }

    bool IsTop { get; }
    bool IsFirst { get; }
    bool IsLast { get; }

    bool HasParent { get; }
    bool HasPrevious { get; }
    bool HasNext { get; }
    bool HasChild { get; }

partial interface ITree<T>
{
    INode<T> InsertChild( T o );

    INode<T> AddChild( T o );
}

partial interface INode<T>
{
    INode<T> InsertPrevious( T o );
    INode<T> InsertNext( T o );
    INode<T> InsertChild( T o );

    INode<T> Add( T o );
    INode<T> AddChild( T o );
}

    bool CanMoveToParent { get; }
    bool CanMoveToPrevious { get; }
    bool CanMoveToNext { get; }
    bool CanMoveToChild { get; }
    bool CanMoveToFirst { get; }
    bool CanMoveToLast { get; }

    void MoveToParent();
    void MoveToPrevious();
    void MoveToNext();
    void MoveToChild();
    void MoveToFirst();
    void MoveToLast();

partial interface ITree<T>
{
    ITree<T> Copy();
    ITree<T> DeepCopy();
}

partial interface INode<T>
{
    ITree<T> Cut();
    ITree<T> Copy();
    ITree<T> DeepCopy();
    void Remove();
}

partial interface ITree<T>
{
    INode<T> this[ T item ] { get; }

    bool Contains( INode<T> node );
    bool Contains( T item );

    ITree<T> Cut( T item );
    ITree<T> Copy( T item );
    ITree<T> DeepCopy( T item );
    bool Remove( T item );
}

partial interface INode<T>
{
    INode<T> this[ T item ] { get; }

    bool Contains( INode<T> node );
    bool Contains( T item );

    ITree<T> Cut( T item );
    ITree<T> Copy( T item );
    ITree<T> DeepCopy( T item );
    bool Remove( T item );
}

public interface IEnumerableCollection<T> : IEnumerable<T>, 
                                                ICollection
{
    bool Contains( T item );
}

public interface IEnumerableCollectionPair<T>
{
    IEnumerableCollection<INode<T>> Nodes { get; }
    IEnumerableCollection<T> Values { get; }
}

partial interface ITree<T> : IEnumerableCollectionPair<T>
{
    IEnumerableCollectionPair<T> All { get; }
    IEnumerableCollectionPair<T> AllChildren { get; }
    IEnumerableCollectionPair<T> DirectChildren { get; }
    IEnumerableCollectionPair<T> DirectChildrenInReverse { get; }
}

partial interface INode<T> : IEnumerableCollectionPair<T>
{
    IEnumerableCollectionPair<T> All { get; }
    IEnumerableCollectionPair<T> AllChildren { get; }
    IEnumerableCollectionPair<T> DirectChildren { get; }
    IEnumerableCollectionPair<T> DirectChildrenInReverse { get; }
}

partial interface ITree<T>
{
    void XmlSerialize( Stream stream );
}

[ Serializable ]
partial class NodeTree<T> : ITree<T>, 
                            INode<T>, ISerializable
{
    public static ITree<T> XmlDeserialize( Stream stream )
}o

partial interface ITree<T>
{
    event EventHandler<NodeTreeDataEventArgs<T>> Validate;
    event EventHandler Clearing;
    event EventHandler Cleared;
    event EventHandler<NodeTreeDataEventArgs<T>> Setting;
    event EventHandler<NodeTreeDataEventArgs<T>> SetDone;
    event EventHandler<NodeTreeInsertEventArgs<T>> Inserting;
    event EventHandler<NodeTreeInsertEventArgs<T>> Inserted;
    event EventHandler Cutting;
    event EventHandler CutDone;
    event EventHandler<NodeTreeNodeEventArgs<T>> Copying;
    event EventHandler<NodeTreeNodeEventArgs<T>> Copied;
    event EventHandler<NodeTreeNodeEventArgs<T>> DeepCopying;
    event EventHandler<NodeTreeNodeEventArgs<T>> DeepCopied;
}

partial interface INode<T>
{
    event EventHandler<NodeTreeDataEventArgs<T>> Validate;
    event EventHandler<NodeTreeDataEventArgs<T>> Setting;
    event EventHandler<NodeTreeDataEventArgs<T>> SetDone;
    event EventHandler<NodeTreeInsertEventArgs<T>> Inserting;
    event EventHandler<NodeTreeInsertEventArgs<T>> Inserted;
    event EventHandler Cutting;
    event EventHandler CutDone;
    event EventHandler<NodeTreeNodeEventArgs<T>> Copying;
    event EventHandler<NodeTreeNodeEventArgs<T>> Copied;
    event EventHandler<NodeTreeNodeEventArgs<T>> DeepCopying;
    event EventHandler<NodeTreeNodeEventArgs<T>> DeepCopied;
}

'''
