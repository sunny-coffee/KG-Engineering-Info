## This class is used to define the hierarchy of the sub-tables.

class Tree:
    def __init__(self,rootObj):
        self.key = rootObj
        self.childs = []
        self.parent = None
 
    def insertChild(self,newNode):
        self.childs.append(newNode)
        newNode.parent = self
 
    def getChilds(self):
        return self.childs
    
    def getParent(self):
        return self.parent

    def setRootVal(self,obj):
        self.key = obj
 
    def getRootVal(self):
        return self.key
