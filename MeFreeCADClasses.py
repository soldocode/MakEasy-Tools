
### MeFreeCADClasses.py
### 2020

from MeFunctions import *

class FCTreeSheet(object):
	def __init__(self,fc_object=None):
		self.FCObject=fc_object
		self.Branches={}
		self.parse()

	def parse(self):
		couples=[]
		obj=self.FCObject
		#root=list(obj.FacesMap.keys())[0]
		fba=get_faces_by_area(obj.Faces,obj.FacesMap['Faces'])
		af=sorted(fba,reverse=True)

		id_key=0

		while id_key<len(af):
			id_block=af[id_key]
			block=obj.FacesByArea[id_block]
			idf1=block[0]
			found=False
			if not found:
				if len(block)==1 and (id_key<len(af)-1):
					id_key+=1
					id_next_block=af[id_key]
					next_block=obj.FacesByArea[id_next_block]
					idf2=next_block[0]
				elif len(block)==2:
					idf2=block[1]

				f1=obj.Faces[idf1]
				f2=obj.Faces[idf2]
				dist=round(f1.distToShape(f2)[0],1)
				if dist==obj.Thk:
					#print('thk:',dist,' ->',idf1,'-',idf2)
					couples.append([idf1,idf2])
			id_key+=1


		couples+=obj.BendedFaces
		print('couples:',couples)
		#branches=[]
		print ('bended faces:',obj.BendedFaces)
		self.Branches=self.get_branches(couples[0][0],obj.FacesMap['Map'],couples)
		#print (branches)
		print ('TreeSheet created.')


	def create_new_branch(self,id_face,face_up,face_down):
		s_up=self.FCObject.Faces[face_up].Surface
		s_down=self.FCObject.Faces[face_down].Surface
		new_branch=Branch()
		new_branch.Class=s_up.__class__.__name__
		new_branch.FaceUp=face_up
		new_branch.FaceDown=face_down
		if new_branch.Class=='Cylinder':
			new_branch.Angle=90
			new_branch.PointOfRotation=s_up.Center
			new_branch.Axis=s_up.Axis
			new_branch.Radius=(s_up.Radius+s_down.Radius)/2
		return new_branch

	def get_branches(self,face_up_from,map,couples):
		next_calls=[]
		#branches=[]
		bb={}
		face_down=None
		for c in couples:
			if face_up_from==c[0]:
				face_down_from=c[1]
				couple=c
			if face_up_from==c[1]:
				face_down_from=c[0]
				couple=c
		print ('...lookin for face up from ',face_up_from)

		links_up=map[face_up_from]
		print ('links up:',links_up)
		for geo_up_from in links_up:
			for p in couples:
				face_up_to=links_up[geo_up_from][0]
				if face_up_to in p:
					print (face_up_to,' found in',p,' with geo id ',geo_up_from)
					print ('...lookin for face down from ',face_down_from)
					links_down=map[face_down_from]
					print('links_down:',links_down)
					for geo_down_from in links_down:
						face_down_to=links_down[geo_down_from][0]
						if face_down_to in p:
							geo_up_to=links_up[geo_up_from][1]
							geo_down_to=links_down[geo_down_from][1]
							if not face_up_from in bb:
								#branch_from=Branch()
								#branch_from.FaceUp=face_up_from
								#branch_from.FaceDown=face_down_from
								#branch_from.Class=self.FCObject.Faces[face_up_from].Surface.__class__.__name__
								bb[face_up_from]=self.create_new_branch(face_up_from,
													          			face_up_from,
															   			face_down_from)
							br_from=bb[face_up_from]
							if not face_up_to in bb:
								#branch_to=Branch()
								#branch_to.FaceUp=face_up_to
								#branch_to.FaceDown=face_down_to
								#branch_to.Class=self.FCObject.Faces[face_up_to].Surface.__class__.__name__
								bb[face_up_to]=self.create_new_branch(face_up_to,
													          		  face_up_to,
															   		  face_down_to)
							br_to=bb[face_up_to]
							j1=br_to.Joints[geo_up_from]=Joint()
							j1.FromBranch=br_from
							j1.ToBranch=br_to
							j1.JoinUp=[geo_up_from,face_up_to,geo_up_to]
							j1.JoinDown=[geo_down_from,face_down_to,geo_down_to]
							j2=br_from.Joints[geo_up_to]=Joint()
							j2.FromBranch=br_to
							j2.ToBranch=br_from
							j2.JoinUp=[geo_up_to,face_up_from,geo_up_from]
							j2.JoinDown=[geo_down_to,face_down_from,geo_down_from]

							print (face_down_to,' found in',p,' with geo id ',geo_down_from)
							#branches.append(dict(face_up_from=face_up_from,
							#					 geo_up_from=geo_up_from,
							#					 face_up_to=face_up_to,
							#					 geo_up_to=links_up[geo_up_from][1],
							#					 face_down_from=face_down_from,
							#					 geo_down_from=geo_down_from,
							#					 face_down_to=face_down_to,
							#					 geo_down_to=links_down[geo_down_from][1]))
							next_calls.append(face_up_to)
							#branches+=get_branches_from_face(face_up_to,map,c)

		c=list(couples)
		c.remove(couple)
		for n in next_calls:
			#branches+=self.get_branches(n,map,c)
			bb.update(self.get_branches(n,map,c))
		return bb

class Branch(object):
	def __init__(self,Class='Plane',Angle=0):
		#self.FCTreeSheet=None
		self.Joints={}
		self.Class=Class # could be Plane or Cylinder
		self.Angle=Angle
		self.PointOfRotation=None
		self.Axis=None
		self.FaceUp=None
		self.FaceDown=None

class Joint(object):
	def __init__(self):
		self.Status='free'
		self.FromBranch=None
		self.ToBranch=None
		self.JoinUP=[0,0,0] #[GeoIdFrom,FaceIdTo,GeoIdTo]
		self.JoinDown=[0,0,0] #[GeoIdFrom,FaceIdTo,GeoIdTo]
